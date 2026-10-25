"""Read-only HOI4 focus -> national spirit/dynamic modifier evidence extraction.

Uses a block AST plus the complete previous occurrence JSONL. It is a static
dependency audit, not an evaluator of DLC gates, branches, scopes or savegames.
Only the output JSON under global-buff-review/data is written.
"""
import bisect
import collections
import hashlib
import json
import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent
BASE = GUIDE / 'vanilla-modifier-catalog'
OUT = BASE / 'global-buff-review/data/focus-spirit-evidence.json'
SUMMARY_OUT = OUT.with_name('focus-spirit-summary.json')
GAME = Path(r'E:\Steam\steamapps\common\Hearts of Iron IV')
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[=!<>?]+|[^\s{}=!<>?#"]+')
NUMBER = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$')
SYMBOL = re.compile(r'[A-Za-z_][A-Za-z_0-9]*$')
PARAM = re.compile(r'\$|\[|\]|^var:|^event_target:')
FOCUS_EFFECT_ENTRYPOINTS = {'completion_reward', 'completion_reward_joint_originator',
                           'completion_reward_joint_member', 'select_effect'}
SKIP_BRANCHES = {
    'limit', 'trigger', 'allowed', 'available', 'visible', 'enable', 'potential',
    'ai_will_do', 'ai_weight', 'ai_weights', 'prerequisites', 'cancel_trigger',
    'bypass', 'abort', 'cancel_if_invalid', 'target_trigger', 'target_root_trigger',
    'modifier', 'targeted_modifier', 'equipment_bonus', 'state_modifier',
    'country_modifier', 'unit_modifiers', 'unit_modifier', 'sub_unit_modifiers',
    'ai_strategy', 'ai_strategy_plan', 'cost',
}
VARIABLE_OPS = {
    'set_variable', 'add_to_variable', 'subtract_from_variable', 'multiply_variable',
    'divide_variable', 'clamp_variable', 'set_variable_to_random',
}
NESTED_TYPES = {
    'equipment_bonus', 'equipment_modifiers', 'targeted_modifier', 'targeted_modifiers',
    'state_modifier', 'state_modifiers', 'unit_modifier', 'unit_modifiers',
    'sub_unit_modifiers', 'field_marshal_modifier', 'corps_commander_modifier',
    'research_bonus', 'country_modifier', 'country_modifiers',
}


class Node:
    __slots__ = ('key', 'op', 'value', 'children', 'parent', 'line', 'end_line')
    def __init__(self, key, line, parent, op=None, value=None, children=None):
        self.key, self.line, self.parent = key, line, parent
        self.op, self.value, self.children = op, value, children
        self.end_line = line


def unquote(token):
    return token[1:-1] if token.startswith('"') and token.endswith('"') else token


def parse(text):
    """Parse assignments and anonymous list atoms while preserving block identity."""
    newlines = [m.start() for m in re.finditer('\n', text)]
    tokens = [(m.group(), bisect.bisect_right(newlines, m.start()) + 1)
              for m in TOKEN.finditer(text) if not m.group().startswith('#')]
    issues = []
    root = Node('<root>', 1, None, children=[])
    def block(parent, index):
        while index < len(tokens):
            token, line = tokens[index]
            if token == '}':
                parent.end_line = line
                return index + 1
            if token == '{':
                node = Node('<anonymous>', line, parent, children=[])
                parent.children.append(node)
                index = block(node, index + 1)
                continue
            if index + 1 < len(tokens) and tokens[index + 1][0] in ('=', '>', '<', '>=', '<=', '!=', '?='):
                op = tokens[index + 1][0]
                if index + 2 >= len(tokens):
                    issues.append({'line': line, 'reason': 'missing assignment value'})
                    return len(tokens)
                value, value_line = tokens[index + 2]
                node = Node(unquote(token), line, parent, op=op)
                parent.children.append(node)
                if value == '{':
                    node.children = []
                    index = block(node, index + 3)
                else:
                    node.value = unquote(value)
                    node.end_line = value_line
                    index += 3
            else:
                parent.children.append(Node(None, line, parent, value=unquote(token)))
                index += 1
        parent.end_line = len(newlines) + 1
        if parent is not root:
            issues.append({'line': parent.line, 'reason': 'unclosed block'})
        return index
    block(root, 0)
    return root, issues


def walk(node):
    for child in node.children or []:
        yield child
        if child.children is not None:
            yield from walk(child)


def path_to(node, stop=None):
    result = []
    current = node.parent
    while current is not None and current is not stop:
        if current.key != '<root>':
            result.append(current.key or '<anonymous>')
        current = current.parent
    return list(reversed(result))


def scalar(node, key):
    for child in node.children or []:
        if child.key == key and child.children is None and child.op == '=':
            return child.value
    return None


def source(path, line):
    return {'file': str(path), 'relative_file': path.relative_to(GAME).as_posix(), 'line': line}


def value_kind(value):
    if value is None:
        return 'missing'
    if NUMBER.fullmatch(value):
        return 'literal_number'
    if value in ('yes', 'no'):
        return 'boolean'
    if PARAM.search(value):
        return 'parameter_or_scoped_expression'
    return 'symbol_or_variable'


def infer_scope(context, initial=None):
    """Conservative current-scope inference; keep source-value binding separate."""
    scope = dict(initial or {'type': 'country', 'identity': 'focus_root', 'reason': 'focus reward starts in country scope'})
    previous = None
    for raw in context:
        key = raw.lower()
        if key in FOCUS_EFFECT_ENTRYPOINTS:
            scope = {'type': 'country', 'identity': 'focus_root', 'reason': key + ' country origin'}
        elif raw == 'ROOT':
            scope = {'type': 'country', 'identity': 'focus_root', 'reason': 'ROOT of the focus effect'}
        elif key in ('prev', 'from') or key.startswith(('prev.', 'from.', 'event_target:', 'var:', 'global_event_target:')):
            scope = {'type': 'unknown', 'identity': raw, 'reason': 'dynamic/relative target not resolved'}
        elif raw.isdigit() and previous not in ('random_list', 'prioritize'):
            scope = {'type': 'state', 'identity': 'state:' + raw, 'reason': 'numeric state scope'}
        elif key in ('capital_scope', 'capital_state') or re.match(r'^(every|random|any|all)_(?:.*_)?state$', key):
            scope = {'type': 'state', 'identity': 'iterator:' + raw, 'reason': 'state target/scope iterator'}
        elif key in ('owner', 'controller', 'overlord', 'faction_leader'):
            scope = {'type': 'country', 'identity': 'derived:' + raw, 'reason': 'country target scope'}
        elif re.match(r'^(every|random|any|all)_(?:.*_)?country$', key):
            scope = {'type': 'country', 'identity': 'iterator:' + raw, 'reason': 'country scope iterator'}
        elif re.match(r'^(every|random|any|all)_(?:.*_)?(?:unit_leader|army_leader|navy_leader|operative|scientist|character)$', key):
            scope = {'type': 'unit_or_character', 'identity': raw, 'reason': 'leader/character scope iterator'}
        elif 'special_project' in key and key.startswith(('every_', 'random_', 'any_')):
            scope = {'type': 'special_project', 'identity': raw, 'reason': 'special-project scope iterator'}
        elif re.fullmatch(r'[A-Z][A-Z0-9]{2}', raw) and raw not in ('NOT', 'AND', 'OR'):
            scope = {'type': 'country', 'identity': 'country:' + raw, 'reason': 'literal country tag scope'}
        previous = key
    return scope


def scope_for_chain(context, chain):
    current = None
    for edge in chain:
        current = infer_scope(edge['call_context'], current)
    return infer_scope(context, current)


def main():
    catalog_path = BASE / 'data/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8-sig'))
    records = catalog['records']
    registry = {r['key'] for r in records}
    canonical = {k.lower(): k for k in registry}
    occurrences = collections.defaultdict(dict)
    occurrence_path = BASE / 'data/occurrences.jsonl'
    scanned_occurrences = 0
    for line in occurrence_path.open(encoding='utf-8'):
        row = json.loads(line)
        scanned_occurrences += 1
        if row['kind'] == 'definition':
            occurrences[row['relative_file']][(row['line'], row['key'])] = row

    manifests, parser_issues = [], []
    def load_ast(path):
        data = path.read_bytes()
        manifests.append({'source': source(path, 1), 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()})
        root, issues = parse(data.decode('utf-8-sig', errors='replace'))
        for issue in issues:
            parser_issues.append(dict(source=source(path, issue['line']), reason=issue['reason']))
        return root

    def modifiers(node, file, object_kind, direct_focus=False):
        found = []
        rel = file.relative_to(GAME).as_posix()
        for item in walk(node):
            key = canonical.get((item.key or '').lower())
            if not key or item.children is not None or item.op != '=':
                continue
            evidence = occurrences[rel].get((item.line, key))
            if evidence is None:
                continue
            ancestry = path_to(item, node)
            nested = next((p for p in reversed(ancestry) if p in NESTED_TYPES), None)
            if 'effect_tooltip' in ancestry:
                payload = 'tooltip_only_not_executed'
            elif object_kind in ('country_spirit', 'hidden_idea'):
                if ancestry == ['modifier']:
                    payload = 'country_modifier'
                elif nested:
                    payload = nested
                else:
                    payload = 'other_nested_payload'
            elif object_kind == 'dynamic_modifier':
                payload = 'dynamic_modifier_value' if not ancestry else (nested or 'nested_dynamic_payload')
            elif object_kind == 'named_modifier':
                payload = 'named_modifier_value' if not ancestry else (nested or 'nested_named_payload')
            elif direct_focus and ancestry == ['modifier']:
                payload = 'country_modifier'
            elif 'add_state_modifier' in ancestry:
                payload = 'state_modifier'
            elif nested:
                payload = nested
            else:
                payload = 'other_nested_payload'
            found.append({'key': key, 'source_key': item.key, 'value': item.value,
                          'value_kind': value_kind(item.value), 'source': source(file, item.line),
                          'context': path_to(item), 'relative_context': ancestry,
                          'payload_type': payload,
                          'country_payload': payload == 'country_modifier',
                          'occurrence_classification_rule': evidence['classification_rule']})
        return found

    objects, object_index, excluded_groups = [], collections.defaultdict(list), collections.Counter()
    def add_object(node, file, kind, idea_group=None):
        uid = kind + ':' + node.key + '@' + file.relative_to(GAME).as_posix() + ':' + str(node.line)
        obj = {'object_uid': uid, 'object_id': node.key, 'object_kind': kind,
               'source': source(file, node.line), 'end_line': node.end_line,
               'source_family': file.relative_to(GAME).as_posix().split('/')[1],
               'idea_group': idea_group, 'modifiers': modifiers(node, file, kind),
               'auxiliary_debug': 'debug' in file.name.lower(),
               'callbacks_not_followed': [{'name': c.key, 'source': source(file, c.line)}
                                          for c in node.children or []
                                          if c.key in ('on_add', 'on_remove', 'on_update') and c.children]}
        obj['modifier_keys'] = sorted({m['key'] for m in obj['modifiers']})
        obj['country_payload_keys'] = sorted({m['key'] for m in obj['modifiers'] if m['country_payload']})
        obj['scope_note'] = ('国家精神直属 modifier；嵌套载荷已分离' if kind == 'country_spirit' else
                             '隐性 ideas 组，单独统计，不与 ideas.country 合并' if kind == 'hidden_idea' else
                             '可应用于国家、地区、单位将领或特殊项目；不能仅凭定义文件认定国家作用域' if kind == 'dynamic_modifier' else
                             '静态/事件命名修正，可能由天气、战斗等机制使用，不能统一视为国家精神')
        objects.append(obj)
        object_index[(kind, node.key)].append(obj)

    for file in sorted((GAME / 'common/ideas').glob('*.txt')):
        root = load_ast(file)
        for ideas in root.children:
            if ideas.key != 'ideas' or ideas.children is None:
                continue
            for group in ideas.children:
                if group.children is None:
                    continue
                for obj in group.children:
                    if obj.children is None:
                        continue
                    if group.key in ('country', 'hidden_ideas'):
                        add_object(obj, file, 'country_spirit' if group.key == 'country' else 'hidden_idea', group.key)
                    else:
                        excluded_groups[group.key] += 1
    for family, kind in [('dynamic_modifiers', 'dynamic_modifier'), ('modifiers', 'named_modifier')]:
        for file in sorted((GAME / 'common' / family).glob('*.txt')):
            root = load_ast(file)
            for obj in root.children:
                if obj.children is not None:
                    add_object(obj, file, kind)
    for name in ('event_modifiers.txt', 'triggered_modifiers.txt'):
        file = GAME / 'common' / name
        if file.exists():
            root = load_ast(file)
            for obj in root.children:
                if obj.children is not None:
                    add_object(obj, file, 'named_modifier')
    object_by_uid = {o['object_uid']: o for o in objects}

    # Collect scripted-effect identifiers before resolving calls in their bodies.
    effect_asts = []
    effect_ids = set()
    for file in sorted((GAME / 'common/scripted_effects').glob('*.txt')):
        root = load_ast(file)
        for item in root.children:
            if item.children is not None:
                effect_ids.add(item.key)
                effect_asts.append((file, item))

    def command_summary(nodes, file):
        result = {'object_references': [], 'effect_calls': [], 'variable_changes': [], 'unresolved': []}
        def visit(item):
            if item.op not in (None, '='):
                return
            key = (item.key or '').lower()
            if key in SKIP_BRANCHES:
                return
            base = {'source': source(file, item.line), 'context': path_to(item)}
            if key == 'effect_tooltip':
                result['unresolved'].append(dict(base, kind='tooltip_only_block_not_executed', command=item.key))
                return
            if item.key in effect_ids:
                call = dict(base, effect_id=item.key, parameterized=item.children is not None,
                            call_value=item.value,
                            arguments={c.key: c.value for c in item.children or [] if c.key and c.children is None})
                result['effect_calls'].append(call)
                return
            if key in ('country_event', 'news_event', 'state_event'):
                result['unresolved'].append(dict(base, kind='event_chain_not_followed', command=item.key,
                                                  value=item.value or scalar(item, 'id')))
                return
            if key in ('add_ideas', 'swap_ideas', 'add_timed_idea', 'add_dynamic_modifier', 'add_country_modifier'):
                target_values = []
                if key == 'add_ideas':
                    target_values = ([item.value] if item.children is None else
                                     [c.value for c in item.children if c.key is None and c.children is None])
                elif key == 'swap_ideas':
                    target_values = [scalar(item, 'add_idea')]
                elif key == 'add_timed_idea':
                    target_values = [scalar(item, 'idea')]
                else:
                    target_values = [scalar(item, 'modifier') or scalar(item, 'name') or item.value]
                kinds = ('country_spirit', 'hidden_idea') if key in ('add_ideas', 'swap_ideas', 'add_timed_idea') else (
                    ('dynamic_modifier',) if key == 'add_dynamic_modifier' else ('named_modifier',))
                for target in target_values or [None]:
                    refs = [obj for kind in kinds for obj in object_index.get((kind, target), [])]
                    ref = dict(base, command=item.key, object_id=target,
                               object_uids=[obj['object_uid'] for obj in refs],
                               object_kinds=sorted({obj['object_kind'] for obj in refs}),
                               explicit_scope_binding=scalar(item, 'scope'),
                               removed_idea=scalar(item, 'remove_idea') if key == 'swap_ideas' else None)
                    if target is None or PARAM.search(target):
                        ref['status'] = 'unresolved_parameter_or_expression'
                    elif not refs:
                        ref['status'] = 'not_in_country_spirit_hidden_dynamic_or_named_index'
                    else:
                        ref['status'] = 'resolved_static_object_reference'
                    result['object_references'].append(ref)
                return
            if key in VARIABLE_OPS:
                changes = []
                if item.children is None:
                    if item.value:
                        changes.append((item.value, None))
                else:
                    explicit = scalar(item, 'var')
                    if explicit:
                        changes.append((explicit, scalar(item, 'value')))
                    else:
                        for child in item.children:
                            if child.children is None and child.key not in ('value', 'min', 'max', 'round', 'integer', 'tooltip'):
                                changes.append((child.key, child.value))
                for variable, value in changes:
                    if variable:
                        result['variable_changes'].append(dict(base, operation=item.key,
                                                              variable=variable, value=value,
                                                              exact_bare_symbol=bool(SYMBOL.fullmatch(variable))))
                return
            for child in item.children or []:
                visit(child)
        for item in nodes:
            visit(item)
        return result

    effects = collections.defaultdict(list)
    for file, item in effect_asts:
        summary = command_summary(item.children, file)
        effects[item.key].append(dict(effect_id=item.key, source=source(file, item.line), **summary))
    del effect_asts

    focuses = []
    for family in ('national_focus', 'continuous_focus'):
        for file in sorted((GAME / 'common' / family).glob('*.txt')):
            root = load_ast(file)
            for item in walk(root):
                if item.key not in ('focus', 'shared_focus', 'joint_focus') or item.children is None:
                    continue
                focus_id = scalar(item, 'id')
                if not focus_id:
                    continue
                rewards = [c for c in item.children if c.key in FOCUS_EFFECT_ENTRYPOINTS and c.children is not None]
                summary = command_summary(rewards, file)
                focus = dict(focus_id=focus_id, focus_uid=file.relative_to(GAME).as_posix() + ':' + str(item.line),
                             source=source(file, item.line), focus_kind=family,
                             auxiliary_debug='debug' in file.name.lower(),
                             direct_modifiers=modifiers(item, file, 'focus', direct_focus=True),
                             **summary)
                focuses.append(focus)

    # Traverse only simple no-argument scripted-effect calls. Calls with argument
    # blocks are retained as unresolved rather than guessing substitutions.
    focus_links, unresolved_calls, variable_links = [], [], []
    dynamic_variables = collections.defaultdict(list)
    for obj in objects:
        if obj['object_kind'] != 'dynamic_modifier':
            continue
        for mod in obj['modifiers']:
            if mod['payload_type'] == 'dynamic_modifier_value' and SYMBOL.fullmatch(mod['value'] or '') and mod['value'] not in ('yes', 'no'):
                dynamic_variables[mod['value']].append((obj, mod))

    for focus in focuses:
        first_link_index = len(focus_links)
        gathered_refs = []
        gathered_vars = []
        gathered_unresolved = []
        visited = set()
        def expand(summary, chain, active):
            gathered_refs.extend((r, chain) for r in summary['object_references'])
            gathered_vars.extend((r, chain) for r in summary['variable_changes'])
            gathered_unresolved.extend(dict(r, via_effects=chain) for r in summary['unresolved'])
            for call in summary['effect_calls']:
                effect_id = call['effect_id']
                if call['parameterized']:
                    unresolved_calls.append(dict(focus_id=focus['focus_id'], focus_source=focus['source'],
                                                kind='parameterized_scripted_effect_not_expanded', call=call,
                                                via_effects=chain))
                    continue
                if effect_id in active:
                    unresolved_calls.append(dict(focus_id=focus['focus_id'], focus_source=focus['source'],
                                                kind='scripted_effect_cycle', call=call, via_effects=chain))
                    continue
                if len(chain) >= 16:
                    unresolved_calls.append(dict(focus_id=focus['focus_id'], focus_source=focus['source'],
                                                kind='scripted_effect_depth_limit', call=call, via_effects=chain))
                    continue
                for effect in effects[effect_id]:
                    identity = (effect_id, effect['source']['file'], effect['source']['line'])
                    if identity in visited:
                        continue
                    visited.add(identity)
                    edge = {'effect_id': effect_id, 'source': effect['source'], 'call_source': call['source'],
                            'call_context': call['context']}
                    expand(effect, chain + [edge], active | {effect_id})
        expand(focus, [], set())
        applied_uids = set()
        applied_scopes = collections.defaultdict(list)
        for ref, chain in gathered_refs:
            link_id = 'L' + str(len(focus_links) + 1)
            link = dict(ref, link_id=link_id, focus_id=focus['focus_id'], focus_uid=focus['focus_uid'],
                        focus_source=focus['source'], via_effects=chain,
                        link_type='focus_scripted_effect_object' if chain else 'focus_direct_object',
                        modifier_keys=sorted({m['key'] for uid in ref['object_uids']
                                              for m in object_by_uid[uid]['modifiers']}))
            link['application_scope'] = scope_for_chain(ref['context'], chain)
            link['country_scope_status'] = ('country_candidate' if link['application_scope']['type'] == 'country' else
                                            'excluded_state_or_object' if link['application_scope']['type'] != 'unknown' else 'unknown')
            # scope= is a source-scope binding, not the recipient, but without
            # evaluating it do not recommend the link as a proven global value.
            if ref['explicit_scope_binding'] and (PARAM.search(ref['explicit_scope_binding']) or ref['explicit_scope_binding'].isdigit()):
                link['country_scope_status'] = 'unknown_explicit_value_scope_binding'
            link['auxiliary_debug'] = focus['auxiliary_debug']
            link['country_global_candidate_keys'] = sorted({
                m['key'] for uid in ref['object_uids'] for m in object_by_uid[uid]['modifiers']
                if not focus['auxiliary_debug'] and not object_by_uid[uid]['auxiliary_debug']
                and link['country_scope_status'] == 'country_candidate'
                and m['payload_type'] in ('country_modifier', 'dynamic_modifier_value', 'named_modifier_value')
            })
            focus_links.append(link)
            applied_uids.update(ref['object_uids'])
            for uid in ref['object_uids']:
                applied_scopes[uid].append(link['application_scope'])
        focus['reachable_object_links'] = [r['link_id'] for r in focus_links[first_link_index:]]
        focus['event_boundaries'] = [r for r in gathered_unresolved if r['kind'] == 'event_chain_not_followed']
        focus['tooltip_only_blocks_skipped'] = [r for r in gathered_unresolved if r['kind'] == 'tooltip_only_block_not_executed']
        for mutation, chain in gathered_vars:
            if not mutation['exact_bare_symbol']:
                continue
            for obj, mod in dynamic_variables.get(mutation['variable'], []):
                # Exact dataflow symbol matching is reliable; object application
                # is separately reported, and no same-country runtime claim made.
                mutation_scope = scope_for_chain(mutation['context'], chain)
                same_scope_application = any(
                    scope['type'] == mutation_scope['type'] == 'country'
                    and scope['identity'] == mutation_scope['identity']
                    and (scope['identity'] == 'focus_root' or scope['identity'].startswith('country:'))
                    for scope in applied_scopes.get(obj['object_uid'], [])
                )
                variable_links.append({
                    'focus_id': focus['focus_id'], 'focus_uid': focus['focus_uid'], 'focus_source': focus['source'],
                    'variable': mutation['variable'], 'operation': mutation['operation'], 'mutation_value': mutation['value'],
                    'mutation_source': mutation['source'], 'mutation_context': mutation['context'], 'via_effects': chain,
                    'object_id': obj['object_id'], 'object_uid': obj['object_uid'], 'object_source': obj['source'],
                    'modifier_key': mod['key'], 'modifier_source': mod['source'],
                    'object_applied_in_same_focus_closure': obj['object_uid'] in applied_uids,
                    'mutation_scope': mutation_scope,
                    'same_static_country_scope_application_in_closure': same_scope_application,
                    'evidence_strength': ('same_focus_static_country_scope_dependency' if same_scope_application else 'exact_symbol_only_scope_unverified'),
                    'auxiliary_debug': focus['auxiliary_debug'] or obj['auxiliary_debug'],
                    'evidence_type': 'exact_bare_variable_symbol_dependency',
                    'scope_and_runtime_status': '变量名精确对应；不同作用域同名变量仍可能无关，未证明本局对象激活或数值已生效',
                })

    by_modifier = {}
    def entry(key):
        return by_modifier.setdefault(key, {
            'country_spirit_sources': [], 'hidden_idea_sources': [], 'dynamic_sources': [], 'named_modifier_sources': [],
            'focus_direct_sources': [], 'focus_object_links': [], 'dynamic_variable_links': [],
        })
    for obj in objects:
        field = {'country_spirit': 'country_spirit_sources', 'hidden_idea': 'hidden_idea_sources',
                 'dynamic_modifier': 'dynamic_sources', 'named_modifier': 'named_modifier_sources'}[obj['object_kind']]
        for mod in obj['modifiers']:
            entry(mod['key'])[field].append({
                'object_id': obj['object_id'], 'object_uid': obj['object_uid'], 'object_kind': obj['object_kind'],
                'source': obj['source'], 'modifier_source': mod['source'], 'payload_type': mod['payload_type'],
                'country_payload': mod['country_payload'], 'value': mod['value'], 'value_kind': mod['value_kind'],
                'auxiliary_debug': obj['auxiliary_debug'],
            })
    for focus in focuses:
        for mod in focus['direct_modifiers']:
            entry(mod['key'])['focus_direct_sources'].append({
                'focus_id': focus['focus_id'], 'focus_uid': focus['focus_uid'], 'source': focus['source'],
                'modifier_source': mod['source'], 'focus_kind': focus['focus_kind'], 'payload_type': mod['payload_type'],
                'country_payload': mod['country_payload'], 'value': mod['value'],
                'auxiliary_debug': focus['auxiliary_debug'],
            })
    for link in focus_links:
        for key in link['modifier_keys']:
            entry(key)['focus_object_links'].append({
                'link_id': link['link_id'], 'focus_id': link['focus_id'], 'focus_uid': link['focus_uid'],
                'source': link['focus_source'], 'reference_source': link['source'],
                'object_id': link['object_id'], 'object_uids': link['object_uids'],
                'object_kinds': link['object_kinds'], 'link_type': link['link_type'],
                'country_scope_status': link['country_scope_status'],
                'application_scope': link['application_scope'],
                'country_global_candidate': key in link['country_global_candidate_keys'],
                'auxiliary_debug': link['auxiliary_debug'],
            })
    for index, link in enumerate(variable_links):
        entry(link['modifier_key'])['dynamic_variable_links'].append({
            'variable_link_index': index, 'focus_id': link['focus_id'], 'source': link['focus_source'],
            'mutation_source': link['mutation_source'], 'object_id': link['object_id'],
            'variable': link['variable'], 'object_applied_in_same_focus_closure': link['object_applied_in_same_focus_closure'],
            'evidence_strength': link['evidence_strength'], 'auxiliary_debug': link['auxiliary_debug'],
        })

    summary_records = {}
    for key, evidence in sorted(by_modifier.items()):
        spirits = [x for x in evidence['country_spirit_sources'] if x['country_payload'] and not x['auxiliary_debug']]
        hidden = [x for x in evidence['hidden_idea_sources'] if x['country_payload'] and not x['auxiliary_debug']]
        direct = [x for x in evidence['focus_direct_sources'] if x['country_payload'] and not x['auxiliary_debug']]
        candidates = [x for x in evidence['focus_object_links'] if x['country_global_candidate'] and not x['auxiliary_debug']]
        dynamics = [x for x in evidence['dynamic_sources'] if x['payload_type'] == 'dynamic_modifier_value' and not x['auxiliary_debug']]
        variable_refs = [x for x in evidence['dynamic_variable_links'] if not x['auxiliary_debug']]
        applied_dynamic_uids = {uid for x in candidates if 'dynamic_modifier' in x['object_kinds'] for uid in x['object_uids']}
        nested = [x for field in ('country_spirit_sources', 'hidden_idea_sources', 'dynamic_sources')
                  for x in evidence[field]
                  if not x['auxiliary_debug'] and x['payload_type'] not in ('country_modifier', 'dynamic_modifier_value')]
        focus_union = candidates + direct
        focus_uids = {x.get('focus_uid') or (x['source']['file'] + ':' + str(x['source']['line'])) for x in focus_union}
        summary_records[key] = {
            'key': key,
            'country_spirit_direct_count': len(spirits),
            'country_spirit_ids': sorted({x['object_id'] for x in spirits}),
            'country_spirit_examples': spirits[:3],
            'focus_country_global_candidate_count': len(candidates),
            'focus_country_global_candidate_link_count': len(candidates),
            'focus_country_global_candidate_unique_focus_count': len(focus_uids),
            'focus_country_global_candidate_focus_ids': sorted({x['focus_id'] for x in focus_union}),
            'focus_country_global_candidate_unique_focus_uids': sorted(focus_uids),
            'focus_country_global_direct_union_evidence_count': len(focus_union),
            'focus_country_global_candidate_examples': candidates[:3],
            'focus_direct_country_count': len(direct),
            'focus_direct_examples': direct[:3],
            'focus_all_paths_count': len(evidence['focus_object_links']),
            'focus_unknown_scope_count': sum(x['country_scope_status'].startswith('unknown') for x in evidence['focus_object_links']),
            'focus_state_or_object_count': sum(x['country_scope_status'] == 'excluded_state_or_object' for x in evidence['focus_object_links']),
            'variable_strong_count': sum(x['evidence_strength'] == 'same_focus_static_country_scope_dependency' for x in variable_refs),
            'variable_weak_count': sum(x['evidence_strength'] == 'exact_symbol_only_scope_unverified' for x in variable_refs),
            'variable_examples': variable_refs[:3],
            'hidden_idea_direct_count': len(hidden),
            'dynamic_definition_count': len(dynamics),
            'country_applied_dynamic_definition_count': sum(x['object_uid'] in applied_dynamic_uids for x in dynamics),
            'excluded_nested_count': len(nested),
            'excluded_nested_examples': nested[:3],
            'debug_auxiliary_count': sum(x.get('auxiliary_debug', False)
                                         for field in ('country_spirit_sources', 'hidden_idea_sources', 'dynamic_sources',
                                                       'named_modifier_sources', 'focus_direct_sources') for x in evidence[field]),
        }

    counts = {
        'registry_keys': len(registry), 'complete_occurrence_rows_read': scanned_occurrences,
        'files_parsed': len(manifests), 'parser_issues': len(parser_issues),
        'objects_by_kind': dict(collections.Counter(o['object_kind'] for o in objects)),
        'empty_objects_by_kind': dict(collections.Counter(o['object_kind'] for o in objects if not o['modifiers'])),
        'keys_by_object_kind': {kind: len({m['key'] for o in objects if o['object_kind'] == kind for m in o['modifiers']})
                               for kind in ('country_spirit', 'hidden_idea', 'dynamic_modifier', 'named_modifier')},
        'country_spirit_direct_country_keys': len({m['key'] for o in objects if o['object_kind'] == 'country_spirit'
                                                  for m in o['modifiers'] if m['country_payload']}),
        'country_spirit_direct_country_keys_excluding_debug': sum(r['country_spirit_direct_count'] > 0 for r in summary_records.values()),
        'focuses_by_kind': dict(collections.Counter(f['focus_kind'] for f in focuses)),
        'direct_focus_keys': len({m['key'] for f in focuses for m in f['direct_modifiers']}),
        'direct_focus_country_keys': len({m['key'] for f in focuses for m in f['direct_modifiers'] if m['country_payload']}),
        'simple_scripted_effect_definitions': sum(len(v) for v in effects.values()),
        'focus_object_links': len(focus_links),
        'focus_object_link_status': dict(collections.Counter(l['status'] for l in focus_links)),
        'focus_object_link_commands': dict(collections.Counter(l['command'] for l in focus_links)),
        'focus_object_link_keys': len({k for link in focus_links for k in link['modifier_keys']}),
        'focus_object_link_scope_status': dict(collections.Counter(l['country_scope_status'] for l in focus_links)),
        'focus_country_global_candidate_keys': sum(r['focus_country_global_candidate_count'] > 0 for r in summary_records.values()),
        'variable_symbol_links': len(variable_links),
        'variable_symbol_keys': len({l['modifier_key'] for l in variable_links}),
        'variable_links_with_object_applied_in_same_closure': sum(l['object_applied_in_same_focus_closure'] for l in variable_links),
        'variable_links_with_same_static_country_scope_application': sum(l['same_static_country_scope_application_in_closure'] for l in variable_links),
        'unresolved_scripted_effect_calls': len(unresolved_calls),
        'unresolved_scripted_effect_kinds': dict(collections.Counter(c['kind'] for c in unresolved_calls)),
        'event_boundaries': sum(len(f['event_boundaries']) for f in focuses),
        'tooltip_only_blocks_skipped': sum(len(f['tooltip_only_blocks_skipped']) for f in focuses),
        'objects_with_callbacks_not_followed': sum(bool(o['callbacks_not_followed']) for o in objects),
        'keys_with_any_evidence': len(by_modifier),
    }
    result = {
        'schema_version': 2, 'analysed_date': '2026-10-25', 'catalog_snapshot_date': catalog.get('analysed_date'), 'game_root': str(GAME),
        'game_version': catalog.get('game_version'),
        'method': '独立块AST + 完整occurrences.jsonl逐行定义证据；不运行或修改原版',
        'coverage_limits': [
            '统计的是本机原版静态可达/定义证据，不代表所有分支同局同时生效或当前国家数值。',
            'ideas.country仅作为国家精神定义；hidden_ideas独立列出；法律、顾问、设计商、军种spirit等其他组不混入。',
            '国家精神直属modifier与equipment_bonus、targeted_modifier、state/unit等嵌套载荷分别统计。',
            'dynamic_modifiers可应用于国家/地区/单位将领/特殊项目，common/modifiers还包含天气战斗等静态机制，定义文件不等于国家作用域。',
            '国策从completion_reward、completion_reward_joint_originator、completion_reward_joint_member、select_effect追踪静态对象引用。联合国策两入口按CWTools规则root=this=country。',
            '仅展开无参数块的scripted_effect调用，最多16层；同一国策到同一定义保留第一条可达调用链，不把多次路径数作为触发次数。',
            '参数化效果、事件后续链、复杂变量/事件目标/数组表达式未求值；未命中不代表原版绝对从未间接使用。',
            'effect_tooltip仅用于显示，不执行；已从国策实际可达链中排除。精神on_add/on_remove/on_update回调未递归执行，定义位置单列。',
            'debug来源保留辅助证据但不进入主摘要。common/modifiers静态天气/战斗等对象仅凭定义不进入国策国家候选。',
            'focus_country_global_candidate_count与link_count均为对象引用链接数；unique_focus_count按candidate加direct来源的focus_uid去重，focus_ids为对应ID集合；不将多链接称为多个国策。',
            '动态变量链只作精确裸变量名的文本数据依赖；同一国策可达应用另标记，未模拟变量作用域或证明本局激活。',
            '直接赋值依赖完整第一轮definition分类，避免把set_variable等同名变量操作误计为修正定义。',
            '多定义同名对象全部保留，不猜测引擎最终覆盖顺序；所有结果保留文件行号。',
        ],
        'counts': counts, 'excluded_idea_groups': dict(excluded_groups),
        'focus_effect_entrypoints': sorted(FOCUS_EFFECT_ENTRYPOINTS),
        'joint_entrypoint_scope_schema': {'file': str(GUIDE / 'references/cwtools-hoi4-config/Config/common/national_focus.cwt'),
                                        'lines': [752, 753, 758, 759],
                                        'meaning': 'joint originator/member奖励均replace_scope root=country this=country'},
        'objects': objects, 'focuses': focuses, 'focus_object_links': focus_links,
        'dynamic_variable_links': variable_links, 'unresolved_effect_calls': unresolved_calls,
        'by_modifier': dict(sorted(by_modifier.items())),
        'records': summary_records,
        'parser_issues': parser_issues, 'source_manifest': manifests,
        'input_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (catalog_path, occurrence_path)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = {k: result[k] for k in ('schema_version', 'analysed_date', 'catalog_snapshot_date', 'game_version',
                                     'method', 'coverage_limits', 'counts', 'excluded_idea_groups', 'parser_issues', 'records')}
    summary['full_evidence_file'] = str(OUT)
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'summary': str(SUMMARY_OUT), 'counts': counts,
                      'excluded_idea_groups': dict(excluded_groups)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
