# triggers 离线参考（598 条）

来源：[CWTools HOI4 配置固定提交](https://github.com/cwtools/cwtools-hoi4-config/tree/297dd69c42aabe10078a8b7ab7f2d07ee631d4ef)。

上游版权：Copyright (c) 2018 tboby；适用 [MIT 许可](../cwtools-hoi4-config/LICENSE)。本文件由上游 `Config/script_documentation.json` 重新排版生成，未独立验证引擎行为。快照取得日期：2026-10-24；其对应的精确游戏版本未知。条目数量不代表引擎接口总量。

描述中的数值、示例和作用域均来自上游，可能存在遗漏或错误；实际开发须以目标游戏版本文档和运行结果复核。

## add_to_temp_array

Scope: `any`  
Target: `none`

```text
Adds an element to a temporary array
Example: add_to_temp_array = {
	array = array_name
	value = 42 #optional, if not defined adds scope
	index = 3 #optional, default is end. otherwise elements are shifted
}
#shorter usage: add_to_temp_array = { array_name = 42 }
```

## add_to_temp_variable

Scope: `any`  
Target: `none`

```text
![MD]
Adds a value, a variable, or a [math expression](script_math_expression.md) to a temporary variable.

### Examples
''' 
add_to_temp_variable = { num_dogs = 42 }
add_to_temp_variable = {
	num_dogs = { value = num_cats  multiply = 2 }
}
''' 

```

## advisor_can_be_fired

Scope: `CHARACTER`  
Target: `none`

```text
"Return true if the character has an advisor role and they can be fired.
Warning: will return false if the character has no advisor role or it does not match the input slot. You should use has_advisor_role trigger first to really test the can_be_fired flag.

Examples:
some_character_scope = {
  advisor_can_be_fired = {
    slot = political_advisor # mandatory if the character has several advisor role
  }
}

some_character_scope = {
  advisor_can_be_fired = yes # or no
}"
```

## agency_upgrade_number

Scope: `COUNTRY`  
Target: `none`

```text
Checks the number of upgrade done in the intelligence agency. 
agency_upgrade_number > 4
```

## ai_has_role_division

Scope: `COUNTRY`  
Target: `none`

```text
check if the ai controlled country has any fielded divisions for a specific role
```

## ai_has_role_template

Scope: `COUNTRY`  
Target: `none`

```text
check if the ai controlled country has any template for a specific role
```

## ai_irrationality

Scope: `COUNTRY`  
Target: `none`

```text
check the ai irrationality value
```

## ai_liberate_desire

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check what liberation desire the country has towards a specified country
```

## ai_wants_divisions

Scope: `COUNTRY`  
Target: `none`

```text
Will compare towards the amount of divisions an ai wants to have.
```

## all_active_scientist

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if all active scientists of the Country in scope matches the triggers.
ex: GER = {
  all_active_scientists = {
	tooltip = my_loc_key # Optional
     ... Character scope triggers ...
  }
}"
```

## all_allied_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if all allied countries meet the trigger. Does not include the country itself. tooltip=key can be defined to override title
```

## all_army_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if All Army Leader of the Country in scope match the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  all_army_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## all_character

Scope: `COUNTRY`  
Target: `none`

```text
check if all characters meets the trigger. tooltip=key can be defined to override title
```

## all_claimant

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if the provided trigger is true for all countries that claims the state in scope.
`tooltip` supports bindable localization.

### Example
''' 
all_claimant = {
	tooltip = my_loc # Optional bindable localization
	has_war_goal = yes
}
''' 
```

## all_collection_elements

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if the triggers are true for all of the elements in the collection.

### Example
''' 
all_collection_elements = {
    collection = {
		input = game:scope
		operators = { controlled_states }
	}
	is_core_of = PREV
}
''' 

```

## all_controlled_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all of the states controlled by the scope country meets the trigger. tooltip=key can be defined to override title
```

## all_core_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if all of the country core states for the scope meets the trigger. tooltip=key can be defined to override title
```

## all_country

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all countries meets the trigger. tooltip=key can be defined to override title
```

## all_country_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if all of the provided countries fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
all_country_of = {
	tooltip = my_loc # Optional bindable localization
	target = { SWE NOR FIN DEN ICE }
	has_defensive_war = yes
}

all_country_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	has_defensive_war = yes
}
''' 

```

## all_country_with_original_tag

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all country with current scope's original tag meets the trigger. Example:
all_country_with_original_tag = { 
  original_tag_to_check = ENG # the trigger check all countries that has this original tag 
  # ... triggers to check 
}
```

## all_enemy_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all enemy countries meet the trigger. tooltip=key can be defined to override title
```

## all_guaranteed_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if every country with current scoped country guarantees. Example:
all_country_with_original_tag = { 
  # ... triggers to check 
}
```

## all_military_industrial_organization

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if all Military Industrial Organisations of the Country in scope match the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  any_military_industrial_organization = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... MIO scope triggers ...
  }
}"
```

## all_navy_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if all Navy Leaders of the Country in scope match the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  all_navy_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## all_neighbor_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all neighbor countries meet the trigger. tooltip=key can be defined to override title
```

## all_neighbor_state

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all neighbor states meets the trigger. tooltip=key can be defined to override title
```

## all_occupied_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all occupied countries meets the trigger. tooltip=key can be defined to override title
```

## all_of

Scope: `any`  
Target: `any`

```text
Runs a loop on an array and check a trigger for each value, if any false returns false. otherwise returns true
Example: all_of = {
	array = array_name
	value = value_name #optional (default 'v') current value in array will be stored in this temp variable
	index = index_name #optional (default 'i') current index in array will be stored in this temp variable
 #trigger 1
 #trigger 2 ...
}
```

## all_of_scopes

Scope: `any`  
Target: `any`

```text
Runs a loop on an array and check a trigger for each scope in it, if any false returns false. otherwise returns true
Example: all_of_scopes = {
	array = array_name
	tooltip = loc #if defined the trigger will output tooltip using this title. loc_NOT will be used if trigger is inside a NOT
 #trigger 1
 #trigger 2 ...
}
```

## all_operative_leader

Scope: `COUNTRY, OPERATION`  
Target: `none`

```text
check if all operatives meets the trigger. tooltip=key can be defined to override title
```

## all_other_country

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all other countries meets the trigger. Excludes current country. tooltip=key can be defined to override title
```

## all_owned_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all owned states meets the trigger. tooltip=key can be defined to override title
```

## all_purchase_contracts

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if all purchase contracts of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  all_purchase_contracts = {
	tooltip = my_loc_key # Optional
     ... Purchase Contract scope triggers ...
  }
}"
```

## all_scientists

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if all scientists of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  all_scientists = {
	tooltip = my_loc_key # Optional
     ... Character scope triggers ...
  }
}"
```

## all_state

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all states meets the trigger. tooltip=key can be defined to override title
```

## all_subject_countries

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if all subject countries meet the trigger. tooltip=key can be defined to override title
```

## all_unit_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if all Unit Leaders of the Country in scope match the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  all_unit_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## alliance_naval_strength_ratio

Scope: `COUNTRY`  
Target: `none`

```text
Compares the estimated naval strength between the scope country, his allies and his enemies.
```

## alliance_strength_ratio

Scope: `COUNTRY`  
Target: `none`

```text
Compares the estimated army strength between the scope country, his allies and his enemies.
```

## always

Scope: `any`  
Target: `any`

```text
always returns specified value
```

## amount_manpower_in_deployment_queue

Scope: `COUNTRY`  
Target: `none`

```text
Checks for amount manpower currently in deploymentview. amount_manpower_in_training > 10
```

## amount_research_slots

Scope: `COUNTRY`  
Target: `none`

```text
check number of research current research slots 
 amount_research_slots > 2
```

## amount_taken_ideas

Scope: `COUNTRY`  
Target: `none`

```text
has current country picked specified amount of ideas. Category and slots is optional.
Excludes national_spirit, hidden, law = yes
amount_taken_ideas = {
	amount < <int> (mandatory)
	categories = { military_staff } (optional)
	slots = { army_chief political_advisor } (optional)
}
```

## and

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
all inside trigger must be true
```

## any_active_scientist

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if at least one active scientist of the Country in scope matches the triggers.
ex: GER = {
  any_active_scientist = {
	tooltip = my_loc_key # Optional
    ... Character scope triggers ...
  }
}"
```

## any_allied_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if any allied country meets the trigger. Does not include the country itself. tooltip=key can be defined to override title
```

## any_army_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if at least one Army Leader of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  any_army_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## any_character

Scope: `COUNTRY`  
Target: `none`

```text
check if any character meets the trigger. tooltip=key can be defined to override title
```

## any_claim

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if there is a claim between a country and all others
```

## any_collection_element

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if the triggers are true for any of the elements in the collection.
If optional parameter `count` is set, then it checks if the number of elements that the trigger is true for is equal or larger than `count`.

### Example
''' 
any_collection_element = {
    collection = {
		input = game:scope
		operators = { controlled_states }
	}
	is_core_of = PREV
}
any_collection_element = {
    collection = {
		input = game:scope
		operators = { controlled_states }
	}
	is_core_of = PREV
	count = 3
}
''' 

```

## any_controlled_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any of the states controlled by the scope country meets the trigger. tooltip=key can be defined to override title
```

## any_core_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if any of the country core states for scope meets the trigger. tooltip=key can be defined to override title
```

## any_country

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any country meets the trigger
```

## any_country_division

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any division meets the trigger. tooltip=key can be defined to override title
```

## any_country_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any of the provided countries fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
any_country_of = {
	tooltip = my_loc # Optional bindable localization
	target = { SWE NOR FIN DEN ICE }
	has_defensive_war = yes
}

any_country_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	has_defensive_war = yes
}
''' 

```

## any_country_with_core

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any country with a core on the scoped state meets the trigger. tooltip=key can be defined to override title
```

## any_country_with_original_tag

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any country with current scope's original tag meets the trigger. Example:
any_country_with_original_tag = { 
  original_tag_to_check = ENG # the trigger check all countries that has this original tag 
  # ... triggers to check 
}
```

## any_country_with_original_tag_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any country that has an original tag that matches any of the provided countries fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
any_country_with_original_tag_of = {
	tooltip = my_loc # Optional bindable localization
	target = { SWE NOR FIN DEN ICE }
	has_defensive_war = yes
}

any_country_with_original_tag_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	has_defensive_war = yes
}
''' 

```

## any_enemy_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any enemy country meets the trigger. tooltip=key can be defined to override title
```

## any_guaranteed_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any country with current scoped country guarantees. Example:
any_guaranteed_country = { 
  # ... triggers to check 
}
```

## any_home_area_neighbor_country

Scope: `COUNTRY`  
Target: `none`

```text
check if any neighbor country in the home area meets the trigger. tooltip=key can be defined to override title
```

## any_military_industrial_organization

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if at least one Military Industrial Organisation of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  any_military_industrial_organization = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... MIO scope triggers ...
  }
}"
```

## any_navy_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if at least one Navy Leader of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  any_navy_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## any_neighbor_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any neighbor country meets the trigger. tooltip=key can be defined to override title
```

## any_neighbor_state

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any neighbor state meets the trigger. tooltip=key can be defined to override title
```

## any_occupied_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any any occupied meets the trigger. tooltip=key can be defined to override title
```

## any_of

Scope: `any`  
Target: `any`

```text
Runs a loop on an array and check a trigger for each value, if any true returns true. otherwise returns false
Example: any_of = {
	array = array_name
	value = value_name #optional (default 'value') current value in array will be stored in this temp variable
	index = index_name #optional (default 'index') current index in array will be stored in this temp variable
 #trigger 1
 #trigger 2 ...
}
```

## any_of_scopes

Scope: `any`  
Target: `any`

```text
Runs a loop on an array and check a trigger for each scope in it, if any true returns true. otherwise returns false
Example: any_of_scopes = {
	array = array_name
	tooltip = loc #if defined the trigger will output tooltip using this title. loc_NOT will be used if trigger is inside a NOT
 #trigger 1
 #trigger 2 ...
}
```

## any_operative_leader

Scope: `COUNTRY, OPERATION`  
Target: `none`

```text
check if any operatives meets the trigger. tooltip=key can be defined to override title
```

## any_other_country

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any other country meets the trigger. Excludes current country. tooltip=key can be defined to override title
```

## any_other_country_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any of the provided countries (except for the current country) fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
any_other_country_of = {
	tooltip = my_loc # Optional bindable localization
	target = { SWE NOR FIN DEN ICE }
	has_defensive_war = yes
}

any_other_country_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	has_defensive_war = yes
}
''' 

```

## any_other_country_with_original_tag_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any country that has an original tag that matches any of the provided countries and isn't the current country fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
any_country_with_original_tag_of = {
	tooltip = my_loc # Optional bindable localization
	target = { SWE NOR FIN DEN ICE }
	has_defensive_war = yes
}

any_country_with_original_tag_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	has_defensive_war = yes
}
''' 

```

## any_owned_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any owned state meets the trigger. tooltip=key can be defined to override title
```

## any_province_building_level

Scope: `STATE`  
Target: `any`

```text
In the current state, checks if any province within the specified limit has a building of the specified level.
Example:
any_province_building_level = {
  province = {
    id = 421  # Only check specific provinces instead of all in state, can specify multiple provinces on multiple lines.
    all_provinces = yes  # default: no. Mutually exclusive with 'id = xxx']
    limit_to_border = yes  # default: no. Only border provinces.
    limit_to_coastal = yes  # default: no. Only coastal provinces.
    limit_to_victory_point = yes  # default: no. Only provinces with > 0 victory points.
    limit_to_naval_base = yes  # default: no. Only provinces with a naval base.
  }
  building = bunker  # Building type.
  level < 3  # Building level to check.
}
```

## any_purchase_contract

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if at least one Purchase contract of the Country in scope matches the triggers. 
tooltip=key can be defined to override title.
ex: GER = {
  any_purchase_contract = {
	tooltip = my_loc_key # Optional
    ... Purchase Contract scope triggers ...
  }
}"
```

## any_scientist

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
"Checks if at least one scientist of the Country in scope matches the triggers. 
tooltip=key can be defined to override title.
ex: GER = {
  any_scientist = {
	tooltip = my_loc_key # Optional
    ... Character scope triggers ...
  }
}"
```

## any_state

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any state meets the trigger. tooltip=key can be defined to override title
```

## any_state_division

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any division meets the trigger. tooltip=key can be defined to override title
```

## any_state_in

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any state in the given category meets the trigger.
tooltip=key can be defined to override title.
The trigger takes one of the followings:
	array: an array of states.
	continent: A continent.
	ai_area: The id of an area.
	strategic_region: The id of an region.

* Note that no default tooltip is available for array and ai_area.
Example:
Check if the trigger is valid in any state in a continent:
any_state_in = {	conteinent = europe
	FOO_TRIGGER = BAR
}
```

## any_state_of

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any of the provided states fulfill the specified triggers.
The `target` supports script constants and `tooltip` supports bindable localization.

### Example
''' 
any_state_of = {
	tooltip = my_loc # Optional bindable localization
	target = { 1 42 1992 }
	controller = {
		has_defensive_war = yes
	}
}

any_state_of = {
    tooltip = my_loc # Optional bindable localization
	target = constant:country_groups:nordics
	controller = {
		has_defensive_war = yes
	}
}
''' 

```

## any_subject_country

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if any subject country meets the trigger. tooltip=key can be defined to override title
```

## any_unit_leader

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if at least one Unit Leader of the Country in scope matches the triggers.
tooltip=key can be defined to override title.
ex: GER = {
  any_unit_leader = {
	tooltip = my_loc_key # Optional
	include_invisible = yes # Optional - default = no
    ... character scope triggers ...
  }
}"
```

## any_war_score

Scope: `COUNTRY`  
Target: `none`

```text
compares the warscore of all wars in a country to see if any fullfills the comparison condition 0-100 - Example: any_war_score > 40
```

## area

Scope: `STATE`  
Target: `none`

```text
check state's strategic area id
```

## armor

Scope: `COMBATANT`  
Target: `none`

```text
Check that average armor level of combatant is over a certain level
```

## army_manpower_in_state

Scope: `COUNTRY`  
Target: `none`

```text
Checks for amount manpower currently the target state with option to specify a type.
Example:
army_manpower_in_state = {
	state = <id> (variables supported)
	amount < <int> (variables supported)
	type > <equipment_type> (armor, infantry, etc.)
```

## attack_skill_level

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
Compares attack skill level of a unit leader.
Example: attack_skill_level > 5
```

## average_stats

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
Compares the average stats for a unit leader.
Example: average_stats > 10
```

## building_count_trigger

Scope: `STATE, COUNTRY`  
Target: `none`

```text
Checks if the current scope has the specified amount of the specified building. 
Usage: <Building> < <int>
Supported buildings: infrastructure, arms_factory, industrial_complex, air_base, supply_node, rail_way, naval_facility, naval_base, bunker, coastal_bunker, stronghold_network, dockyard, anti_air_building, synthetic_refinery, fuel_silo, radar_station, mega_gun_emplacement, rocket_site, naval_supply_hub, naval_headquarters, nuclear_reactor, nuclear_reactor_heavy_water, commercial_nuclear_reactor, nuclear_facility, air_facility, land_facility, dam, dam_mountain, cataract_dam_mountain, canal_kiel, canal_panama, energy_infrastructure, industrial_infrastructure, landmark_big_ben, landmark_colosseum, landmark_cristo_redentor, landmark_eiffel_tower, landmark_statue_of_liberty, landmark_kremlin, landmark_hofburg_palace, landmark_berlin_reichstag, landmark_berlin_volkshalle, landmark_taj_mahal, landmark_sadabad_complex, landmark_hagia_sophia, landmark_forbidden_city, landmark_nanjing_presidential_palace, landmark_nanjing_presidential_palace_prc, landmark_nanjing_presidential_palace_gen, landmark_great_wall_section, landmark_tokyo_imperial_palace, landmark_national_diet, landmark_hakko_ichiu, landmark_prague_castle, landmark_bojnice_castle.
```

## buyer

Scope: `PURCHASE_CONTRACT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check the buyer country. Example: buyer = GER
```

## can_assign_supportive_scientist_to_faction

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the faction from the country in scope has a free slot for a supportive scientist for the country with the specialization type
ex:
Ger = {
	can_assign_supportive_scientist_to_faction = specialization_land
}"
```

## can_be_captured

Scope: `CHARACTER`  
Target: `none`

```text
can_be_captured = yes/no - Checks if the current character can be captured while deployed in a division
```

## can_be_country_leader

Scope: `COUNTRY, CHARACTER`  
Target: `none`

```text
Returns true if specified character has a least one country leader role.

Example:
can_be_country_leader = GER_erwin_rommelGER_erwin_rommel = { can_be_country_leader = yes }
```

## can_build_railway

Scope: `any`  
Target: `any`

```text
Checks if a railway can be built according to specifications. Example:
can_build_railway = {
  build_only_on_allied = yes # No by default. If yes and the effect scope is country, it will only build on allied territories for the country

  # You can specify a weight function that will be used in pathing. The scope will be the controller of the province it is trying to path to.
  # A negative value will make it not to path to that controller.
  # Non-negative values will be used as a path cost for that province.
  controller_priority = {
    base = 1

    modifier = {
      tag = MAN
      add = 2
    }
  }

  # The following options are used for picking a path. You can specify multiple options and it will pick in following order:
  fallback = yes # Default no. If yes, each option will try to fallback to next one.
  # option 1: List of provinces to draw railways. If fallback = yes uses start and end provinces of the path as fallback in option 2.
  path = { 10 20 30 40 }
  # option 2: Specify start & end province IDs. It will pick the shortest path. If provinces are not valid and if fallback = yes it will use states of those provs and use in option 3.
  start_province = 42
  target_province = 84
  # option 3: Specify start & end state IDs. It will pick provinces with the best node (capital > nodes > naval )
  start_state = 50
  target_state = 100
}

```

## can_construct_building

Scope: `STATE`  
Target: `none`

```text
"Checks if the country (as ROOT) and state in scope can build a building in the state.
ex:
GER = {
	65 = {
		can_construct_building = land_facility
	}
}"
```

## can_declare_war_on

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if the country could potentially declare a war on the target ( according to game rules, relationship, etc... ). Example can_declare_war_on = GER
```

## can_research

Scope: `COUNTRY`  
Target: `none`

```text
check if country can research technology
```

## can_select_trait

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
check if leader can select a trait
```

## career_profile_check_medal

Scope: `any`  
Target: `any`

```text
Checks if the required medal is achieved and collected
```

## career_profile_check_playthrough_ratio

Scope: `any`  
Target: `any`

```text
Compares the ratio (first/second) of two playthrough values to a number
```

## career_profile_check_playthrough_value

Scope: `any`  
Target: `any`

```text
Compares a playthrough value to a number
```

## career_profile_check_points

Scope: `any`  
Target: `any`

```text
Compares a career points value to a number
```

## career_profile_check_ratio

Scope: `any`  
Target: `any`

```text
Compares the ratio (first/second) of two career profile values to a number
```

## career_profile_check_ribbon

Scope: `any`  
Target: `any`

```text
Checks if the required ribbon is achieved and collected
```

## career_profile_check_value

Scope: `any`  
Target: `any`

```text
Compares a career profile value to a number
```

## career_profile_has_player_flag

Scope: `any`  
Target: `any`

```text
Checks if the flag is set for the local player
```

## career_profile_set_temp_playthrough_variable

Scope: `any`  
Target: `none`

```text
Sets a temporary variable to a value or another variable
Example: career_profile_set_temp_playthrough_variable = {
var = num_dogs
	value = num_dogs_in_career_profile
}
```

## career_profile_set_temp_variable

Scope: `any`  
Target: `none`

```text
Sets a temporary variable to a value or another variable
Example: career_profile_set_temp_variable = {
var = num_dogs
	value = num_dogs_in_career_profile
}
```

## casualties

Scope: `COUNTRY`  
Target: `none`

```text
Check the amount of casualties a country has suffered in all of it's wars
```

## casualties_inflicted_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks the casualties infliced by the speficied country to the scopped country.
E.g. true if Germany has been inflicted more than 200k casualties by Poland:
GER = {
  casualties_inflicted_by = {
    opponent = POL
    thousands > 200
  }
}
```

## casualties_k

Scope: `COUNTRY`  
Target: `none`

```text
Check the amount of casualties in thousands a country has suffered in all of it's wars
```

## check_expr

Scope: `any`  
Target: `any`

```text
![MD]
Evaluates a math expression and returns true when the result is non-zero.

### Parameters
- `Expression`: Any supported math expression.

### Example
''' 
check_expr = { value = 2  add = 3  greater_than = 4 }
''' 

```

## check_variable

Scope: `any`  
Target: `any`

```text
"Compares a variable to a number or another variable
ex:
check_variable = {
	var = varname
	value = 12	# accepts variables
	compare = equals
	# possible values for compare :
	# less_than, less_than_or_equals
	# greater_than, greater_than_or_equals
	# equals, not_equals
	tooltip = loc_str_id_with_LEFT_and_RIGHT  #localized text with LEFT and/or RIGHT tokens in it
}
# some shorter versions :
check_variable = { varname = 0 }
check_variable = { varname > 12 }
check_variable = { varname < 42 }
check_variable = { varname > another_varname }
"
```

## civilwar_target

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
civilwar target is ( for civil wars checks )
```

## clamp_temp_variable

Scope: `any`  
Target: `none`

```text
clamps a temp variable between two values/variables
```

## clear_temp_array

Scope: `any`  
Target: `none`

```text
Clears the contents of a temporary array
Example: clear_temp_array = array_name
```

## collection_contains

Scope: `any`  
Target: `any`

```text
![MD]
Checks if the provided collection contains all the provided elements. Possible types to check for are:
- Countries

### Example
''' 
collection_contains = {
    collection = game:all_countries
	countries = { ENG GER }
}
collection_contains = {
    collection = game:all_countries
	country = FRA
}
''' 

```

## collection_size

Scope: `any`  
Target: `any`

```text
![MD]
Compares size of a collection to a value

NOTE! Comparison is inclusive, so "value > X" actually means "value >= X" etc.!!!

### Example
''' 
collection_size = {
	input = collection_id # see the documentation in common/collections for detailed info
	value > N # supported operators: <, >, =
	value < M # multiple comparisons are allowed!
	value < VAR # variables can be used
}
''' 

```

## command_power

Scope: `COUNTRY`  
Target: `none`

```text
Checks if available command power is more or less that specified value 
 command_power > 1.5
```

## command_power_daily

Scope: `COUNTRY`  
Target: `none`

```text
Checks if daily command power increase is more or less that specified value 
 command_power_daily > 1.5
```

## compare_autonomy_progress_ratio

Scope: `COUNTRY`  
Target: `none`

```text
check if autonomy progress ratio is higher than value, example:
compare_autonomy_progress_ratio > 0.5
```

## compare_autonomy_state

Scope: `COUNTRY`  
Target: `none`

```text
check if autonomy state is higher than other one, example:
compare_autonomy_state > puppet
```

## compare_ideology_with_faction

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Compares the ideology support of the country's ruling party for the ideology of the faction it wants to join

### Example
''' 
compare_ideology_with_faction = {
	value > 0.5
	leader = FROM
}
''' 

```

## compare_intel_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compare the intel of the scoped country with the specified one:
GER = {
  # is true if all predicates are satisfied
  compare_intel_with = { 
    target = POL
    civilian_intel > 0.5  # GER has at least 0.5 more civ. intel than POL
    army_intel = 0  # GER has as much army intel as POL
    navy_intel < 0  # POL has more navy intel than GER
    # airforce_intel is not specified and thus ignored in the comparison
  }
}

```

## compliance

Scope: `STATE`  
Target: `any`

```text
Compares the current compliance level of a state to a value. Example: compliance > 50 
```

## compliance_speed

Scope: `STATE`  
Target: `any`

```text
Compares the current compliance speed of a state to a value. Example: compliance_speed > 50 
```

## conscription_ratio

Scope: `COUNTRY`  
Target: `none`

```text
Checks conscription ratio of the country compared to target conscription ratio.

```

## contract_contains_equipment

Scope: `PURCHASE_CONTRACT`  
Target: `none`

```text
"Check if contract contains equipment category, equipment archetype or equipment.
Example:
    contract_contains_equipment = infantry_equipment"
```

## controls_province

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check controller for province
```

## controls_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, CAPITAL`

```text
check controller for state(s)
```

## convoy_threat

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
A trigger to check convoy threat for a country. Controlled by NAVAL_CONVOY_DANGER defines. Returns a value between 0 and 1. Example convoy_threat > 0.5 
```

## core_compliance

Scope: `COUNTRY`  
Target: `any`

```text
Compares the core (average of all occupied states) compliance value of occupied_country_tag that is occuppied by the country in current scope.
Example: 
core_compliance = { 
 occupied_country_tag = ITA 
 value > 35 
}
```

## core_resistance

Scope: `COUNTRY`  
Target: `any`

```text
Compares the core (average of all occupied states) resistance value of occupied_country_tag that is occuppied by the country in current scope.
Example:
core_resistance = { 
 occupied_country_tag = ITA 
 value > 35 
}
```

## count_in_collection

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks the size of a given collection.
	Note: unit and building and manpower are mutually exclusive

	### Example
	''' 
	count_in_collection = {
		collection = {
			input = game:scope
			operators = { faction_members }
			name = FACTION
		}
		unit = armor  # (optional) checks the number of subunits that have the correct equipment type
		buildings = {industrial_complex } # (optional) checks the number of building types in total
		manpower = yes # (optional, default: no) checks the number of deployed manpower
		equipment_ratio = 0.9 (optional, only works with land units default 0) what percentage of equipment the division needs to atleast have to be counted
		unit_category = { marine marine_commando category_fighter }(optional) checks the number of sub units that match a certain sub unit definition / category
		stockpile = light_tank_equipment (optional) counts the amount of a certain archetype in the countries stockpile
		size > 10
	}
	''' 
	
```

## count_triggers

Scope: `any`  
Target: `none`

```text
Returns true if the specified number of sub-triggers return true
count_triggers = { amount = 2 <trigger> <trigger> <trigger> }
```

## country_exists

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if the specified country exist
```

## current_conscription_amount

Scope: `COUNTRY`  
Target: `none`

```text
Checks the current conscription amount of the country.

```

## custom_override_tooltip

Scope: `any`  
Target: `none`

```text
![MD]
An `AND` trigger that has an overridden custom tooltip.
A positive tooltip can be set with `tooltip` and the tooltip to be used inside a NOT can be set with `not_tooltip`.
If no positive tooltip is provided and the root key is a localization key (not a formatter, see [formatted localization](script_concept_documentation.md#formatted-localization)),
then a negative tooltip will be generated by appending `_NOT` to the root localization for the positive tooltip.
Both tooltip and `not_tooltip` are [bindable localizations](script_concept_documentation.md#bindable-localization).

### Examples
''' 
custom_override_tooltip = {
	tooltip = MY_TOOLTIP # Simple loc key tooltip
	not_tooltip = MY_TOOLTIP_NOT
	<other triggers>
}
''' 
''' 
custom_override_tooltip = {
	tooltip = MY_TOOLTIP
	# Implicit:
	#not_tooltip = MY_TOOLTIP_NOT
	<other triggers>
}
''' 
''' 
custom_override_tooltip = {
	tooltip = {
		localization_key = MY_TOOLTIP # Root look key
		IMPORTANT_QUESTION = { # ID IMPORTANT_QUESTION in MY_TOOLTIP will get value:
			localization_key = MEANING_OF_LIFE # Root loc key in IMPORTANT_QUESTION
			ANSWER = "42" # ID ANSWER in IMPORTANT_QUESTION will get value 42
		}
		JUST_AS_IMPORTANT = OR_NOT # ID JUST_AS_IMPORTANT in MY_TOOLTIP will get value OR_NOT
	}
	# Implicit:
	# not_tooltip = {
	#	localization_key = MY_TOOLTIP_NOT
	#	IMPORTANT_QUESTION = {
	#		localization_key = MEANING_OF_LIFE
	#		ANSWER = "42"
	#	}
	#	JUST_AS_IMPORTANT = OR_NOT
	#}
	<other triggers>
}
''' 

```

## custom_trigger_tooltip

Scope: `any`  
Target: `none`

```text
![MD]
Alias for [custom_override_tooltip](#custom_override_tooltip) trigger (see that trigger for more info). Kept for backward compatibility.
Prefer [custom_override_tooltip](#custom_override_tooltip) instead.
```

## date

Scope: `any`  
Target: `none`

```text
checks for a specific date
```

## days_since_capitulated

Scope: `COUNTRY`  
Target: `none`

```text
Checks the number of days since the country last capitulated, even if it is no longer capitulated.
	If it has not ever capitulated, the value is extremely large.
	It is recommended to combine this with has_capitulated = yes when you specifically want to ignore non-active capitulations.
Examples:
	HOL = { has_capitulated = yes days_since_capitulated > 60 } # The Netherlands has been capitulated for more than two months
	FRA = { has_capitulated = yes days_since_capitulated < 21 } # France has capitulated sometime within the past three weeks
	GER = { OR = { has_capitulated = no days_since_capitulated > 14 } } # Germany is not both actively and recently capitulated

```

## days_since_last_strategic_bombing

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks the days since last strategic bombing.
days_since_last_strategic_bombing < 10

```

## deal_completion

Scope: `PURCHASE_CONTRACT`  
Target: `none`

```text
Check value of purchase contract completion. Example: deal_completition < 0.6
```

## debug_math_expr

Scope: `any`  
Target: `any`

```text
![MD]
Evaluates a math expression and writes the numeric result to the tooltip.

Always returns true and is intended for debugging scripts.

### Parameters
- `Expression`: Any supported math expression.

### Example
''' 
debug_math_expr = { value = 120  add = 15  clamp = { min = 0  max = 100 } }
''' 

```

## decryption_progress

Scope: `COUNTRY`  
Target: `none`

```text
checks decryption ratio against a country. Example: 
decryption_progress = { 
 target = GER
 value > 0.5
} 
#or decryption_progress@GER as variable

```

## defense_skill_level

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
Compares defense skill level of a unit leader.
Example: defense_skill_level > 5
```

## difficulty

Scope: `any`  
Target: `none`

```text
check if the difficulty is above or below specified value 0-2 (difficulty enum). Example: difficulty > 0 (above easy)
```

## dig_in

Scope: `COMBATANT`  
Target: `none`

```text
check if we have digin level (lowest)
```

## distance_to

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check distance between two states
```

## divide_temp_variable

Scope: `any`  
Target: `none`

```text
![MD]
Divides a temporary variable by a value, another variable, or a [math expression](script_math_expression.md).

### Examples
''' 
divide_temp_variable = { num_dogs = 2 }
divide_temp_variable = {
	num_dogs = { value = num_cats  add = 1 }
}
''' 

```

## division_has_battalion_in_template

Scope: ``  
Target: `none`

```text
checks if division template has the subunit type.
```

## division_has_majority_template

Scope: ``  
Target: `none`

```text
checks if division template has majority of subunit type.
```

## divisions_in_border_state

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of divisions in specified state owned by current country.
```

## divisions_in_state

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of divisions in specified state owned by current country. 
divisions_in_state = { 
  state = state_id 
  size > 42 
  type = unit type eg. infantry, armor (optional) 
  unit = specific unit eg. mountaineers, light_tank (optional) 
}
```

## enemies_naval_strength_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the estimated navy strength between the scope country and all its enemies
```

## enemies_strength_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the estimated army strength between the scope country and all its enemies
```

## energy_ratio

Scope: `COUNTRY`  
Target: `none`

```text
energy_ratio > 0.8 - Compare current energy fulfilment to the factories, with 1 being 100% and 0 being 0%
```

## estimated_intel_max_armor

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares estimated max armor based on intel. Example: estimated_intel_max_armor = { tag = ITA value > 1 }
```

## estimated_intel_max_piercing

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares estimated max armor based on intel. Example: estimated_intel_max_piercing = { tag = ITA value > 1 }
```

## exists

Scope: `COUNTRY`  
Target: `none`

```text
Check if the current country exist. The country of the scope you are in. Example: DEN = { exists = yes }
```

## faction_goal_fulfillment

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks fulfillment of a faction goal for the current country's faction

### Examples
''' 
TAG = {
	faction_goal_fulfillment = {
		goal = goal_id
		value > X # supports > and <, can accept variables, can be repeated multiple times
	}
}
''' 

```

## faction_influence_rank

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks influence rank in the faction of the current country

### Examples
''' 
TAG = {
	faction_influence_rank < 5
}
''' 

```

## faction_influence_ratio

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
 Checks influence ratio of current country in the faction

### Examples
''' 
 TAG = {
	faction_influence_ratio > 0.1
}
''' 

```

## faction_influence_score

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
 Checks influence value of current country in the faction

### Examples
''' 
 TAG = {
	faction_influence_score > 100
}
''' 

```

## faction_manifest_fulfillment

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks manifest fulfillment value of current country's faction manifest

### Examples
''' 
TAG = {
	faction_manifest_fulfillment > VALUE
}
''' 

```

## faction_power_projection

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks power value of current country's faction projection

### Examples
''' 
TAG = {
	faction_power_projection > VALUE
}
''' 

```

## faction_upgrade_level

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks the active faction member upgrade against the specified upgrade. works with >, <, = 
### Examples
''' 
TAG = {
	faction_upgrade_level > upgrade_token
}
''' 

```

## fastest_unit

Scope: `COMBATANT`  
Target: `none`

```text
check if fastest unit of combatant is over this limit
```

## fighting_army_strength_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the total army fighting strength between the scope country and the one set with 'tag'

Example 1:
fighting_army_strength_ratio = {
	tag = TAG
	ratio > 0.7 # can be '<','>' or '='
}

Example 2:
fighting_army_strength_ratio = {
	tag = TAG
	ratio > VARIABLE # can be '<','>' or '='
}
```

## find_highest_in_array

Scope: `any`  
Target: `any`

```text
Runs a loop on for each element of an array, finds the highest value and stores result in temp variables
Example: find_highest_in_array = {
	array = array_name
	value = value_name #optional (default 'v') highest value in array will be stored in this temp variable
	index = index_name #optional (default 'i') index of highest value in array will be stored in this temp variable
}
```

## find_lowest_in_array

Scope: `any`  
Target: `any`

```text
Runs a loop on for each element of an array, finds the lowest value and stores result in temp variables
Example: find_lowest_in_array = {
	array = array_name
	value = value_name #optional (default 'v') lowest value in array will be stored in this temp variable
	index = index_name #optional (default 'i') index of lowest value in array will be stored in this temp variable
}
```

## focus_progress

Scope: `COUNTRY`  
Target: `none`

```text
checks focus progress example:
 focus_progress = { focus = id progress > 0.5 }
```

## foreign_manpower

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check the amount of foreign garrison manpower we have
```

## free_building_slots

Scope: `STATE`  
Target: `none`

```text
checks building for available construction levels 
free_building_slots = { 
	building = building_type 
	size > 5 
	include_locked = yes # Optional - only to be used for buildings using Shared Slots. 
	province = 42 #will check province buildings if specified 
}
```

## frontage_full

Scope: `COMBATANT`  
Target: `none`

```text
check if sides front is full or can get more reinforcements
```

## fuel_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the fuel ratio to a variable.
Example: fuel_ratio > 0.5
```

## game_rules_allow_achievements

Scope: `any`  
Target: `none`

```text
Returns true if all of the active game rule options allow achievements.
```

## garrison_manpower_need

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check the amount of manpower needed by garrisons
```

## get_highest_scored_country_temp

Scope: `COUNTRY`  
Target: `none`

```text
calculates the highest scored country that is defined in a country scorer and sets it to a variable. Example: 
get_highest_scored_country_temp = { 
  scorer = scorer_id 
  var = var_name # variable name that the result will be stored. default is highest_scored_country 
}
```

## get_sorted_scored_countries_temp

Scope: `COUNTRY`  
Target: `none`

```text
calculates & sorts all countries in a country scorer and stores them and their scores in temp arrays. Example: 
get_sorted_scored_countries_temp = { 
  scorer = scorer_id # id that is used in country scorer  array = array_name # a name to store sorted countries as a temp array (default to sorted_country_list) 
  scores = array_name # corresponding score temp array for countries stored in array (default to country_list_scores) 
}
```

## get_supply_vehicles_temp

Scope: `COUNTRY`  
Target: `none`

```text
sets a temp variable to the number of supply vehicles in stockpile or that are needed. example 
get_supply_vehicles_temp = { 
	var = num_vehicles #variable to set 
	type = truck #can be truck or train 
	need = yes #default no. If yes, gets the number of needed vehicles 
} 

```

## gives_military_access_to

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if country gives military access to specified country
```

## hardness

Scope: `COMBATANT`  
Target: `none`

```text
check lowest/highest hardness level on combatant
```

## has_ability

Scope: `CHARACTER`  
Target: `any`

```text
does unit leader have the abilityCheck if a unit leader has the ability.
Example: has_ability = force_attack
```

## has_active_mission

Scope: `COUNTRY`  
Target: `none`

```text
check if country has an active mission with specified ID. has_active_mission = my_test_mission
```

## has_active_resistance

Scope: `STATE`  
Target: `any`

```text
returns true if state has an active resistance (above zero)
```

## has_active_rule

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the country's faction has a specific active rule

### Examples
''' 
TAG = {
	has_active_rule = rule_key
}
''' 

```

## has_added_tension_amount

Scope: `COUNTRY`  
Target: `none`

```text
Compare if the country has added above or below the specified ammount of tension
```

## has_advisor_role

Scope: `CHARACTER`  
Target: `none`

```text
has_advisor_role = 'character_slot_name' - Checks if the character in scope has an advisor role for the given slot
```

## has_air_experience

Scope: `COUNTRY`  
Target: `none`

```text
Compares current country's air experience with right side value.
 has_air_experience < <value>
```

## has_air_ledger

Scope: `CHARACTER`  
Target: `none`

```text
has_air_ledger = yes/no - Checks if the current character has an air ledger
```

## has_allowed_idea_with_traits

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has allowed ideas with specific traits more than limit. Example: 
has_available_idea_with_traits = { 
	idea = head_of_intelligence # trait names. can be a list of traits in { } 
	limit = 1 
	characters = yes/no - only runs this trigger on characters 
	ignore = generic_head_of_intelligence # if specified, these ideas will be ignored. can be a list of ideas in { }
} 

```

## has_annex_war_goal

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks a country has annex war goal on another country
```

## has_any_captured_general

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
Checks if any of the generals of the scoped country is captured by another country

### Examples
''' 
FRA = {
	has_any_captured_general = yes
}
''' 

```

## has_any_custom_difficulty_setting

Scope: `any`  
Target: `any`

```text
Returns true if the game has any custom difficulty on
```

## has_any_general_captured_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if the scoped country has any unit leader captured by the target country

### Examples
''' 
FRA = {
	has_any_general_captured_by = GER # This will be true if any of France's generals are captured by Germany
}
''' 

```

## has_any_grand_doctrine

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if any grand doctrine is currently assigned to the given folder

	### Examples
	''' 
	TAG = {
		has_any_grand_doctrine = land
	}
	''' 
	
```

## has_any_license

Scope: `COUNTRY`  
Target: `any`

```text
Country has any active licenses
Example: has_any_license = yes
```

## has_any_power_balance

Scope: `COUNTRY`  
Target: `none`

```text
checks if country has any active power balance

Example:
has_any_power_balance = yes/no
```

## has_army_experience

Scope: `COUNTRY`  
Target: `none`

```text
Compares current country's army experience with right side value.
 has_army_experience < <value>
```

## has_army_ledger

Scope: `CHARACTER`  
Target: `none`

```text
has_army_ledger = yes/no - Checks if the current character has an army ledger
```

## has_army_manpower

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of manpower of selected type, additionally of a specified type
```

## has_army_size

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of divisions, additionally of a specified type
```

## has_artillery_ratio

Scope: `COMBATANT`  
Target: `none`

```text
"Check that ratio of atrillery battalions in the composition of a side of combating troops are over a certain level.
For example:
has_artillery_ratio > 0.1"
```

## has_attache

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Has attaché from any other country
```

## has_attache_from

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Has attaché from specified country
```

## has_autonomy_state

Scope: `COUNTRY`  
Target: `none`

```text
check if country currently has an autonomy state, example:
has_autonomy_state = puppet
```

## has_available_idea_with_traits

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has available ideas with specific traits more than limit. Example: 
has_available_idea_with_traits = { 
	idea = head_of_intelligence # trait names. can be a list of traits in { } 
	limit = 1 
	characters = yes/no - only runs this trigger on characters 
	ignore = generic_head_of_intelligence # if specified, these ideas will be ignored. can be a list of ideas in { }
} 

```

## has_bombing_war_support

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check value of bombing malus to war support 0-1: Example has_bombing_war_support < 0.1
```

## has_border_war

Scope: `STATE, COUNTRY`  
Target: `any`

```text
Checks if a there is any border wars for country/state
```

## has_border_war_between

Scope: `any`  
Target: `any`

```text
Checks if a there is a border war between two states
```

## has_border_war_with

Scope: `STATE, COUNTRY`  
Target: `any`

```text
Checks if a there is a border against a state/country
```

## has_breakthrough_points

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the country in scope has enough breakthroughs within a given specialization.
specialization = <specialization_token>
value = <point>
ex: GER = {
	  has_breakthrough_points = {
	    specialization = specialization_nuclear
		value = 1
      }
	}
"
```

## has_built

Scope: `COUNTRY`  
Target: `none`

```text
checks country has built a set number (at least) of a certain type of building since taking goal 
has_built = { 
  type = building_type 
  value = 42 
}
```

## has_capitulated

Scope: `COUNTRY`  
Target: `none`

```text
checks if the country has capitulated
```

## has_captured_operative

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if a country has a captured an operative ( supports scoped variables )
has_captured_operative = GER/yes/no

```

## has_carrier_airwings_in_own_combat

Scope: `COMBATANT`  
Target: `none`

```text
Check if carrier has airplanes that are part of the current combat
```

## has_carrier_airwings_on_mission

Scope: `COMBATANT`  
Target: `none`

```text
check if side has a career with air wings on a mission
```

## has_casualties_war_support

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check value of casualties malus to war support 0-1: Example has_casualties_war_support < 0.1
```

## has_cavalry_ratio

Scope: `COMBATANT`  
Target: `none`

```text
"Check that ratio of cavalry battalions in the composition of a side of combating troops are over a certain level.
For example:
has_cavalry_ratio > 0.5"
```

## has_character

Scope: `COUNTRY`  
Target: `none`

```text
Returns true if scoped country has character.

Example:
has_character = GER_erwin_rommel
```

## has_character_flag

Scope: `CHARACTER`  
Target: `any`

```text
has a character flag been setCheck flag val date set and days since set.
Example: has_unit_leader_flag = test_flag
has_character_flag = { 
	flag = <name> (mandatory)
	value < <int> (optional)
	date > <date> (optional)
	days > <int> (optional)
}
```

## has_civil_war

Scope: `COUNTRY`  
Target: `none`

```text
check if participant in civil war as revolter or target
```

## has_collaboration

Scope: `COUNTRY`  
Target: `none`

```text
checks the collaboration in a target country with our currently scoped country. Example: 
has_collaboration = { 
 target = GER
 value > 0.5
} 
#or has_collaboration@GER as variable

```

## has_combat_modifier

Scope: `COMBATANT`  
Target: `none`

```text
check if combatant has modifier
```

## has_completed_custom_achievement

Scope: `any`  
Target: `any`

```text
"Return true if the input achievement is found in currently loaded mods, and if this achievement has been completed (either in current game or in a previous one)

Example:
has_completed_custom_achievement = {
	mod = my_mod_unique_id # set in common/achievements files
	achievement = my_achievement_token
}"
```

## has_completed_faction_goal

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the country's faction has successfully completed a goal

### Examples
''' 
TAG = {
	has_completed_faction_goal = goal_id
}
''' 

```

## has_completed_focus

Scope: `COUNTRY`  
Target: `none`

```text
has country completed focus
```

## has_completed_goal

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the country was a member of a faction when a specific goal was completed.
Persists across faction disband/recreate, unlike has_completed_faction_goal.

### Examples
''' 
TAG = {
	has_completed_goal = goal_id
}
''' 

```

## has_completed_subdoctrine

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if the current country has ever completed the specified subdoctrine (even if it was later switched out).

	### Examples
	''' 
	TAG = {
		has_completed_subdoctrine = mobile_infantry
	}
	''' 
	
```

## has_completed_track

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if the given subdoctrine track has been completed

	### Examples
	''' 
	TAG = {
		has_completed_track = infantry
	}
	''' 
	
```

## has_contested_owner

Scope: `STATE, COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if a state has the specified country as a contested owner.
The trigger can be used either from a country or a state scope and accepts the other as parameter.
The trigger is localized with a localization environment containing `Country` and `State`.

### Example
The following example has the same end result and localization.
''' 
42 = {
	has_contested_owner = GER
}
GER = {
	has_contested_owner = 42
}
''' 
Standard scope accessors can also be used:
''' 
### Assuming current scope is a state and FROM is a country scope
has_contested_owner = FROM
''' 

```

## has_convoys_war_support

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check value of convoys sunk malus to war support 0-1: Example has_convoys_war_support < 0.1
```

## has_core_occupation_modifier

Scope: `COUNTRY`  
Target: `any`

```text
has an occupation modifier that applies to average resistance/compliance
Example: 
has_core_occupation_modifier = { 
 occupied_country_tag = ITA 
 modifier = token 
}
```

## has_cosmetic_tag

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has specific cosmetic tag set.
Example: INS = { has_cosmetic_tag = INS1 }
```

## has_country_custom_difficulty_setting

Scope: `COUNTRY`  
Target: `any`

```text
Returns true if the game has any custom difficulty on the scope nation
```

## has_country_flag

Scope: `COUNTRY`  
Target: `any`

```text
has country flag been set.Check flag val date set and days since set.
Example: has_country_flag = test_flag
has_country_flag = { 
	flag = <name> (mandatory)
	value < <int> (optional)
	date > <date> (optional)
	days > <int> (optional)
}
```

## has_country_leader

Scope: `COUNTRY`  
Target: `none`

```text
check if country has leader with specified ID. Don't localize this. Tooltip only for debug.
has_country_leader = {
	ruling_only = yes/no (default = yes)
	character = <string> # recommended criteria
	name = <string> # alternative criteria
	id = <ID> # alternative criteria
}
```

## has_country_leader_ideology

Scope: `COUNTRY`  
Target: `none`

```text
Checks the Ideology of the active country leader
```

## has_country_leader_with_trait

Scope: `COUNTRY`  
Target: `none`

```text
check if current country leader has specified trait.
has_country_leader_with_trait = big_fat_idiot
```

## has_custom_difficulty_setting

Scope: `any`  
Target: `any`

```text
Returns true if the game has the specified custom difficulty on: 
Example: has_custom_difficulty_setting = TheAxisIndustry
```

## has_damaged_buildings

Scope: `COUNTRY`  
Target: `none`

```text
check for damaged buildings of nation
```

## has_decision

Scope: `COUNTRY`  
Target: `none`

```text
check if country has active selected decision
```

## has_defensive_war

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is country at defensive war
```

## has_defensive_war_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
One country has defensive war against other country.
```

## has_deployed_air_force_size

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of aircrafts, additionally of a specified type
```

## has_design_based_on

Scope: `COUNTRY`  
Target: `none`

```text
check if country has a buildable non-obsolete design based on an archetype
```

## has_dlc

Scope: `any`  
Target: `none`

```text
Checks if player has a DLC.
Example: has_dlc = "name of the dlc"
```

## has_doctrine

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if the given grand doctrine or subdoctrine is currently active for the country.

	### Examples
	''' 
	TAG = {
		has_doctrine = mobile_warfare # Grand doctrine
	}
	TAG = {
		has_doctrine = mobile_infantry # Subdoctrine
	}
	''' 
	
```

## has_done_agency_upgrade

Scope: `COUNTRY`  
Target: `none`

```text
has country done this intelligence agency upgrade (to its highest level)
```

## has_dynamic_modifier

Scope: `STATE, COUNTRY, CHARACTER`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if scope has a dynamic modifier.

### Example 1
''' 
has_dynamic_modifier = dynamic_modifier_name
''' 

### Example 2
''' 
has_dynamic_modifier = {
	modifier = dynamic_modifier_name
	scope = GER #optional, if the original modifier has been targeted
}
''' 

```

## has_elections

Scope: `COUNTRY`  
Target: `any`

```text
Checks the country's politics on allowing elections. has_elections = yes
```

## has_enemy_naval_control

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if any enemy has enough naval dominance to assert control in certain strategic region.

### Examples
''' 
TAG = {
	has_enemy_naval_control = REGION_ID
}
''' 

```

## has_enough_influence_for_leadership

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the current country has enough political influence to become faction leader

### Examples
''' 
TAG = {
	has_enough_influence_for_leadership = yes
}
''' 

```

## has_equipment

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of equipment stored
```

## has_event_target

Scope: `any`  
Target: `any`

```text
checks if current scope or global scope has the specified event target saved
```

## has_facility_specialization

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the country in scope has a facility with specialization.
ex:
SOV = {
	has_facility_specialization = specialization_nuclear
}"
```

## has_faction_goal

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the country's faction has an active or completed goal

### Examples
''' 
TAG = {
	has_faction_goal = goal_id
}
''' 

```

## has_faction_military_unlocked

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Whether the faction has unlocked the military operations

### Examples
''' 
TAG = {
	has_faction_military_unlocked = yes
}
''' 

```

## has_faction_research_unlocked

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Whether the faction has unlocked the research

### Examples
''' 
TAG = {
	has_faction_research_unlocked = yes
}
''' 

```

## has_faction_template

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the current country is in a faction with a template

### Examples
''' 
TAG = {
	has_faction_template = template_id
}
''' 

```

## has_finished_collecting_for_operation

Scope: `COUNTRY`  
Target: `any`

```text
checks if finished collecting of resources for an operation.
Example: 
has_finished_collecting_for_operation = { 
 target = ITA 
 operation = operation_infiltrate_armed_forces_navy}
```

## has_flanked_opponent

Scope: `COMBATANT`  
Target: `none`

```text
check if side has flanked their opponent
```

## has_focus_tree

Scope: `COUNTRY`  
Target: `none`

```text
Does current country have the specified focus tree.
```

## has_fuel

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of fuel
example:
has_fuel > 500
```

## has_full_control_of_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, CAPITAL`

```text
check controller for state(s)
```

## has_game_rule

Scope: `any`  
Target: `none`

```text
Checks if a game rule is set to a particular option.
Example:
has_game_rule = {
	rule = GER_can_remilitarize_rhineland
	option = yes
}
```

## has_global_flag

Scope: `any`  
Target: `any`

```text
has global flag been set.Check flag val date set and days since set.
Example: has_global_flag = test_flag
has_global_flag = { 
	flag = <name> (mandatory)
	value < <int> (optional)
	date > <date> (optional)
	days > <int> (optional)
}
```

## has_government

Scope: `COUNTRY`  
Target: `none`

```text
does country government (ruling party) belong to ideology group
```

## has_guaranteed

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if country has guaranteed specified country
```

## has_id

Scope: `CHARACTER`  
Target: `none`

```text
check unit leader has specified ID. Don't localize this. Tooltip only for debug.
```

## has_idea

Scope: `COUNTRY`  
Target: `none`

```text
check if country has idea
```

## has_idea_with_trait

Scope: `COUNTRY`  
Target: `none`

```text
check if country has idea with specified trait
```

## has_ideology

Scope: `CHARACTER`  
Target: `none`

```text
has_ideology = stalinism - Checks if the current character has a country leader role matching the sub-ideology
```

## has_ideology_group

Scope: `CHARACTER`  
Target: `none`

```text
has_ideology_group = communism - Checks if the current character has a country leader role matching the ideology group
```

## has_industry_to_become_leader

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the current country exceeds the faction leader in number of factories

### Examples
''' 
TAG = {
	has_industry_to_become_leader = yes
}
''' 

```

## has_intelligence_agency

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
has country created an Intelligence Agency
```

## has_legitimacy

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check scope country legitimacy 0-100: Example has_legitimacy < 60
```

## has_license

Scope: `COUNTRY`  
Target: `any`

```text
Country has specific active license
Example: has_license = {
	from = TAG # has license from this country, optional
	 #if archetype is specified equipment should not be specified
	archetype = light_tank_chassis #any light tank chassis license
	equipment = { # classical equipment reference
		type = light_tank_equipment_2
		version = 0 # optional: omit to match any version of the type
	}
}
```

## has_manpower

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of manpower
```

## has_manpower_for_recruit_change_to

Scope: `COUNTRY`  
Target: `none`

```text
check if manpower is enough to switch recruitment laws not to be negative
```

## has_manpower_to_become_leader

Scope: `COUNTRY`  
Target: `any`

```text
![MD]
Checks if the current country exceeds the current faction leader and its subjects in deployed manpower

### Examples
''' 
TAG = {
	has_manpower_to_become_leader = yes
}
''' 

```

## has_market_access_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if the country has market access with another country. Example: has_market_access_with = GER
```

## has_mastery

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if any track of the given type has at least X mastery.

	### Examples
	''' 
	TAG = {
		has_mastery = {
			amount = 200
			track = infantry
		}
	}
	''' 
	
```

## has_mastery_level

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if the country has reached the specified number of mastery levels (rewards) for the given subdoctrine

	### Examples
	''' 
	TAG = {
		has_mastery_level = {
			amount = 2
			sub_doctrine = mobile_infantry
		}
	}
	''' 
	
```

## has_max_planning

Scope: `COMBATANT`  
Target: `none`

```text
check if side has maximal planning bonus
```

## has_military_access_to

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check country has military access to specified country
```

## has_military_industrial_organization

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the Country in scope has a  Military Industrial Organisation matching the input token.
Can use variable as input.
ex: 
GER = { 
  has_military_industrial_organization = infantry_mio_token
  has_military_industrial_organization = var:my_mio_var
}"
```

## has_mined

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks the mines planted by the country of the parent scope on the coastline of the target countryE.g. true if Germany has more than 1000 mines around Poland coast:
GER = {
  has_mined = {
    target = POL
    value > 1000
  }
}
```

## has_mines

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if a region has amount of mines.
has_mines = {
    region = region_id
    amount = amount_of_mines
}

```

## has_mio_equipment_type

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has the input equipment type.
(possible values can be found in script_enum_equipment_bonus_type and in common/equipment_groups)
ex:
mio:my_mio = {
	has_mio_equipment_type = my_equipment_type_token
}"
```

## has_mio_flag

Scope: `INDUSTRIAL_ORG`  
Target: `any`

```text
"Check if flag has been set within the military industrial organization in scope.
May checks on the value or date/days since last modified date.
Examples:
has_mio_flag = my_flag
has_mio_flag = {
	flag = my_flag (mandatory)
	value < 12 (optional)
	date > 1936.3.25 (optional, compare with the date where the flag was last modified )
	days > 365 (optional, compare with the number of days since the flag was last modified )
}"
```

## has_mio_number_of_completed_traits

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Make comparaison on the number of unlocked traits of the military industrial organization in the scope.
Can use < or > to compare the value with either a fixed value or from a variable.
ex:
var:my_mio_var = {
	has_mio_number_of_completed_traits > 5
	has_mio_number_of_completed_traits < 2
	has_mio_number_of_completed_traits > var:my_number_var
}"
```

## has_mio_policy

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has an allowed policy matching the input token.
ex:
mio:my_mio = {
	has_mio_policy = my_policy_token
}"
```

## has_mio_policy_active

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has an allowed matching the input token, which is currently attached to the MIO.
ex:
mio:my_mio = {
	has_mio_policy_active = my_policy_token
}"
```

## has_mio_research_category

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has the input research category.
ex:
mio:my_mio = {
	has_mio_research_category = my_research_category_token
}"
```

## has_mio_size

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Make comparaison on the size of the military industrial organization in the scope.
Can use < or > to compare the value with either a fixed value or with a variable.
ex:
var:my_mio_var = {
	has_mio_size > 5
	has_mio_size < 2
	has_mio_size > var:my_number_var
}"
```

## has_mio_trait

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has a trait matching the input token.
ex:
mio:my_mio = {
	has_mio_trait = my_trait_token
	has_mio_trait = {
		trait = my_trait_token
	}
}"
```

## has_nationality

Scope: `CHARACTER`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks whether the operative has the specified nationality.
NOTE: this is invalid on non-operatives.
Examples:
has_nationality = GER

```

## has_naval_control

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
Checks if friendly nations and country scope together has enough naval dominance to assert control in strategic region.

### Examples
''' 
TAG = {
	has_naval_control = REGION_ID
}
''' 

```

## has_naval_invasion_against_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if the scoped country has a naval invasion against the specified state.
Example 1:
has_naval_invasion_against_state = <STATE_ID>
Example 2:
 has_naval_invasion_against_state = {
   state = <STATE_ID>
   preparation > 0.0  # (optional: preparation percentage, with a default value of 0.0)
   activated = no   # (optional: if set, also check if invasion is activated or not)
}
```

## has_navy_experience

Scope: `COUNTRY`  
Target: `none`

```text
Compares current country's navy experience with right side value.
 has_navy_experience < <value>
```

## has_navy_ledger

Scope: `CHARACTER`  
Target: `none`

```text
has_navy_ledger = yes/no - Checks if the current character has a navy ledger
```

## has_navy_size

Scope: `COUNTRY`  
Target: `none`

```text
Checks for amount of ships, additionally of a specified type, archetype, or sub unit definition.

Examples:
	has_navy_size = { size > 10 type = convoy } # Must have more than 10 convoys.
	has_navy_size = { size < 1 archetype = ship_hull_light } # Must not have any ships with light hulls.
	has_navy_size = { size > 39 unit = heavy_cruiser } # Must have 40 or more heavy cruisers.
	has_navy_size = { size < 100 } # Must have fewer than 100 ships of any type.
```

## has_non_aggression_pact_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if country has non aggression pact with the specified country
```

## has_occupation_modifier

Scope: `STATE`  
Target: `any`

```text
compares occupied country that creates resistance to a tag. Example: has_occupation_modifier = modifier_name
```

## has_offensive_war

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is country at offensive war
```

## has_offensive_war_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
One country has offensive war against other country.
```

## has_offensive_war_without_friend

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is country at offensive war without specific ally present
```

## has_officer_name

Scope: ``  
Target: `none`

```text
"checks if division has an officer with the provided name key.
Examples:
	has_officer_name = FIN_nikke_parmi
"
```

## has_operation_token

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if a country has a specific token against another country
has_operation_token = {
	tag = GER
	token = some_token_id
}
```

## has_opinion

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check what opinion the country has towards a specified country
```

## has_opinion_modifier

Scope: `COUNTRY`  
Target: `none`

```text
check if a country has the opinion modifier
```

## has_political_power

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of political power
```

## has_power_balance

Scope: `COUNTRY`  
Target: `none`

```text
checks if power balance is active for country

Example:
has_power_balance = {
	id = power_balance_id
}
```

## has_power_balance_modifier

Scope: `any`  
Target: `none`

```text
checks if the power balance has a modifier added to it

Example:
has_power_balance_modifier = {
	id = power_balance_id
	modifier = static_modifier_id
}
```

## has_project_flag

Scope: `SPECIAL_PROJECT`  
Target: `any`

```text
"Check if flag has been set within the special project in scope.
May checks on the value or date/days since last modified date.
Examples:
has_project_flag = my_flag
has_project_flag = {
	flag = my_flag (mandatory)
	value < 12 (optional)
	date > 1936.3.25 (optional, compare with the date where the flag was last modified )
	days > 365 (optional, compare with the number of days since the flag was last modified )
}"
```

## has_railway_connection

Scope: `any`  
Target: `any`

```text
Checks for an existing rail connection. Uses same params as can_build_railway. Example:
has_railway_connection = {
  build_only_on_allied = yes # No by default. If yes and the effect scope is country, it will only build on allied territories for the country

  # The following options are used for picking a path. You can specify multiple options and it will pick in following order:
  fallback = yes # Default no. If yes, each option will try to fallback to next one.
  # option 1: List of provinces to draw railways. If fallback = yes uses start and end provinces of the path as fallback in option 2.
  path = { 10 20 30 40 }
  # option 2: Specify start & end province IDs. It will pick the shortest path. If provinces are not valid and if fallback = yes it will use states of those provs and use in option 3.
  start_province = 42
  target_province = 84
  # option 3: Specify start & end state IDs. It will pick provinces with the best node (capital > nodes > naval )
  start_state = 50
  target_state = 100
}


```

## has_railway_level

Scope: `any`  
Target: `any`

```text
Checks if a state contains a railway at or above the specified level. Example:
has_railway_level = {
  level = 3
  state = 1234
}

```

## has_relation_modifier

Scope: `COUNTRY`  
Target: `any`

```text
Country has specified relation modifier when dealing with _target_ county
Example: has_relation_modifier = {
	target = TAG # has license from this country, optional
	modifier = static_modifier_here
	}
}
```

## has_reserves

Scope: `COMBATANT`  
Target: `none`

```text
check if side has reserves waiting
```

## has_resistance

Scope: `STATE`  
Target: `any`

```text
returns true if state has a resistance
```

## has_resources_amount

Scope: `STATE`  
Target: `none`

```text
checks for amount of resources in state
Example:
has_resources_amount = {
	resource = chromium
	amount > 10
	state = 31 (optional - can be used in state scope instead)
	delivered = no # (optional, default: no) check the actual delivered amount from the state to its controller, with all modifiers applied
```

## has_resources_in_collection

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks for amount of resources in a given collection.

	### Example
	''' 
	has_resources_in_collection = {
		collection = {
				game:scope
				operators =  { country_and_all_subjects }
		}
		resource = chromium
		amount > 10
		extracted = yes # (optional, default: no) checks extracted amount instead of country balance
		buildings = no # (optional, default: no) checks only amount from local buildings instead of country balance
		Note: extracted and buildings are mutually exclusive
	}
	''' 
	
```

## has_resources_in_country

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	checks for amount of resources in country (the balance by default)
	Example:
	''' 
	has_resources_in_country = {
		resource = chromium
		amount > 10
		only_imported = no # (optional, default: no) checks only imported resources instead of country balance
		extracted = no # (optional, default: no) checks extracted amount instead of country balance
		buildings = no # (optional, default: no) checks only amount from local buildings instead of country balance
	}
	''' 
	
```

## has_resources_rights

Scope: `STATE, COUNTRY`  
Target: `none`

```text
Checks for resources rights in state.Warning! this always returns false if the state has no resource.
Example:
has_resources_rights = {
	state = 60 # optional - can be used in state scope instead
	receiver = GER # optional - can be used in country scope instead
	resources = {steel oil} # optional - if not provided checks all resources.
```

## has_rule

Scope: `any`  
Target: `none`

```text
Checks if a rule set for a country.
Example: has_rule = can_puppet
```

## has_scientist_level

Scope: `CHARACTER`  
Target: `none`

```text
"Checks if the scientist of the character in scope matches the skill level condition for a specialization. Supports < > = operators.
level = <int>
specialization = <specialization_token>
ex: my_character = {
	  has_scientist_level = {
	    level > 2
	    specialization = specialization_nuclear
      }
	}
"
```

## has_scientist_specialization

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the country in scope has a scientist with a skill level of at least 1 in specialization.
ex:
SOV = {
	has_scientist_specialization = specialization_nuclear
}"
```

## has_shine_effect_on_focus

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
Check if country has shine effect on focus (either manually achieved or by being worked on).

Note that tooltips are only shown in debug mode.

### Example
''' 
has_shine_effect_on_focus = GER_prioritize_economic_growth
''' 

```

## has_stability

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check value of stability 0-1: Example has_stability < 0.6
```

## has_start_date

Scope: `any`  
Target: `none`

```text
Compare the initial start date of current game.
```

## has_state_category

Scope: `STATE`  
Target: `none`

```text
Check if state has a specific state category
```

## has_state_flag

Scope: `STATE`  
Target: `any`

```text
has state flag been setCheck flag val date set and days since set.
Example: has_state_flag = test_flag
has_state_flag = { 
	flag = <name> (mandatory)
	value < <int> (optional)
	date > <date> (optional)
	days > <int> (optional)
}
```

## has_subdoctrine_in_track

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Checks if any subdoctrine is currently assigned to (any instance of) the given track

	### Examples
	''' 
	TAG = {
		has_subdoctrine_in_track = infantry
	}
	''' 
	
```

## has_subject

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if the country has for subject the given country
```

## has_tactic

Scope: `COUNTRY`  
Target: `none`

```text
![MD]
	Check if the given tactic is unlocked (or active by default) for the country.

	### Examples
	''' 
	TAG = {
		has_tactic = tactic_masterful_blitz
	}
	''' 
	
```

## has_tech

Scope: `COUNTRY`  
Target: `none`

```text
check if country has technology
```

## has_tech_bonus

Scope: `COUNTRY`  
Target: `any`

```text
checks if the country has a bonus for the specified technology or category
Example:
has_tech_bonus = {
	technology =  <tech>
	category = <tech cat>
	}
```

## has_template

Scope: `COUNTRY`  
Target: `none`

```text
Check if country has a division template of specific name
```

## has_template_ai_majority_unit

Scope: `COUNTRY`  
Target: `none`

```text
check if country has a division template that is majority of specific unit using AI's priorities rather than visual
```

## has_template_containing_unit

Scope: `COUNTRY`  
Target: `none`

```text
check if country has a division template that contains a specific unit
```

## has_template_majority_unit

Scope: `COUNTRY`  
Target: `none`

```text
check if country has a division template that is majority of specific unit
```

## has_terrain

Scope: `COUNTRY`  
Target: `none`

```text
Checks if a country has any province of the specified terrain type.
Example: has_terrain = mountain
```

## has_trait

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
check if sides leader has trait
```

## has_truce_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
has_truce_with = yes/no - Checks if the country has truce with the specified country
```

## has_unit_leader

Scope: `COUNTRY`  
Target: `none`

```text
check if country has unit leader with specified ID. Don't localize this. Tooltip only for debug.
```

## has_unit_leader_flag

Scope: `CHARACTER`  
Target: `any`

```text
This trigger is deprecated in favor of has_character_flag (which does the same)has a character flag been setCheck flag val date set and days since set.
Example: has_unit_leader_flag = test_flag
has_unit_leader_flag = { 
	flag = <name> (mandatory)
	value < <int> (optional)
	date > <date> (optional)
	days > <int> (optional)
}
```

## has_unit_type

Scope: `COMBATANT`  
Target: `none`

```text
"Check if the combatant has at least one of the provided unit types.
For example:
has_unit_type = amphibious_mechanized
"
```

## has_variable

Scope: `any`  
Target: `any`

```text
Checks if a variable exists in a scope
```

## has_volunteers_amount_from

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares number of volunteers from the country. Example: has_volunteers_amount_from = { tag = ITA count > 1 }
```

## has_war

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is country at war
```

## has_war_support

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check value of war_support 0-1: Example has_war_support < 0.6
```

## has_war_together_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Are the countries fighting on the same side of a war
```

## has_war_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is countries at war
```

## has_war_with_major

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is country at war with a major
```

## has_war_with_wargoal_against

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country has a war started with a wargoal against the target.
Example 1:
has_war_with_wargoal_against = {
  target = GER
  type = take_state  # (optional: if not specified any wargoal will do)
}
Example 2:
has_war_with_wargoal_against = GER  # (any wargoal will do)
```

## has_wargoal_against

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country has a wargoal against the target.
Example 1:
ENG = { has_wargoal_against = GER }
Example 2:
ENG = {
  has_wargoal_against = {
    target = GER
    type = take_state  # (optional: if not specified any wargoal will do)
  }
}
```

## hidden_trigger

Scope: `STATE, COUNTRY, CHARACTER, COMBATANT, ACE, STRATEGIC_REGION, OPERATION, INDUSTRIAL_ORG, PURCHASE_CONTRACT, RAID_INSTANCE, SPECIAL_PROJECT, FACTION`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
![MD]
A hidden trigger, that will not be displayed in the tooltip.
The trigger can still be evaluate when generating a tooltip.
This might be required in the following cases:

* The trigger has a side effect (e.g. temporary variables).
* The trigger uses random numbers (e.g. acts on a random state)

There are three possible evaluation techniques to use when computing tooltips for
hidden_triggers:

* `eval` - Standard evalulation of the trigger.
This is most likely what you need if you have a trigger that has side effects or random parts.
* `no_eval` - If you have no random parts or side effects, then this will give you a slightly faster computation of the tooltip.
* `legacy` - Previous behaviour that is similar to `eval` but a lot less predictable.
Using this explicitly is very likely a bug.

#### Examples
''' 
hidden_trigger = {
	tooltip_evaluation = eval
	set_temp_variable = { unlock_compare = 0 }			
	all_collection_elements = {
		collection = {
			input = game:scope
			operators =  { faction_members }
		}
		add_to_temp_variable = { unlock_compare = num_armies }
	}
}
''' 

''' 
hidden_trigger = {
	tooltip_evaluation = no_eval
	add_political_power = 10
}
''' 
```

## ic_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the ratio of total industrial capacity between the scope country and the one set with 'tag'
```

## ideology_support_trigger

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if the current scope has the specified ideology above the specified amount.
Usage: <Ideology> < <float>
Supported Ideologies: democratic, communism, fascism, neutrality.
```

## if

Scope: `any`  
Target: `none`

```text
if_, CIfTrigger, A conditional trigger
if = { limit = { <triggers> } <trigger> }
```

## impassable

Scope: `STATE`  
Target: `any`

```text
checks if a state is impassable
```

## intel_level_over

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compare the absolute, percentage based, intel level the scoped country has over
the specified one:
GER = {
  # is true if all predicates are satisfied
  intel_level_over = { 
    target = POL
    civilian_intel > 0.5  # GER has more than 50% civ. intel over POL
    army_intel = 0  # GER has no army intel over POL
    navy_intel > 0  # GER has at least some navy intel over POL
    # airforce_intel is not specified and thus ignored in the comparison

    # NOTE: since we are comparing the intel level of a country over another,
    # checking for values less than 0 does not make sense
    # NOTE: since we are comparing percentages, using values greater than 1
    # does not make sense.
  }
}

```

## is_active_decryption_bonuses_enabled

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if the country activated their active cipher decryption bonuses. Example is_active_decryption_bonuses_enabled = GER
```

## is_active_scientist

Scope: `CHARACTER`  
Target: `any`

```text
"Checks if the scientist of the character in scope is assigned to a project
is_scientist_active = <bool>
ex: my_character = {
        is_scientist_active = yes
        is_scientist_active = no
	}
"
```

## is_advisor

Scope: `CHARACTER`  
Target: `none`

```text
is_advisor = yes/no - Checks if the current character is an advisor
```

## is_ai

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is AI controlled.
```

## is_air_chief

Scope: `CHARACTER`  
Target: `none`

```text
_is_air_chief = yes/no - Checks if the character in scope is hired as an air chief
```

## is_ally_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if a country is ally with another country. will check if two countries are same/in same faction/has subject master relation
Example: is_ally_with = ITA 

```

## is_amphibious_invasion

Scope: `COMBATANT`  
Target: `none`

```text
check if combat is at night
```

## is_army_chief

Scope: `CHARACTER`  
Target: `none`

```text
is_army_chief = yes/no - Checks if the character in scope is hired as an army chief
```

## is_army_leader

Scope: `CHARACTER`  
Target: `none`

```text
is_army_leader = yes/no - Checks if the current character is a army leader
```

## is_assigned

Scope: `CHARACTER`  
Target: `none`

```text
is_assigned = yes/no - Checks if the current unit leader is assigned to command an army/navy
```

## is_attacker

Scope: `COMBATANT`  
Target: `none`

```text
check if attacker side in combat
```

## is_border_conflict

Scope: `STATE`  
Target: `any`

```text
checks if a state is in border conflict
```

## is_border_war

Scope: `CHARACTER, COMBATANT`  
Target: `any`

```text
Checks if a the combatant or leader has a border war
```

## is_capital

Scope: `STATE`  
Target: `none`

```text
Is scope state a capital. 169 = { is_capital = yes }
```

## is_character

Scope: `CHARACTER`  
Target: `none`

```text
Checks whether the character in scope matches the character in input
```

## is_character_slot

Scope: `CHARACTER`  
Target: `none`

```text
alias of has_advisor_role
```

## is_claimed_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if state is claimed by country
```

## is_coastal

Scope: `STATE`  
Target: `none`

```text
check if state is coastal
```

## is_controlled_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if state is controlled by
```

## is_core_of

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if state is core of country
```

## is_corps_commander

Scope: `CHARACTER`  
Target: `none`

```text
is_corps_commander = yes/no - Checks if the current character is a corps commander
```

## is_country_leader

Scope: `CHARACTER`  
Target: `none`

```text
is_country_leader = yes/no - Checks if the current character is a country leader
```

## is_cryptology_department_active

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
has country an active cryptology department
```

## is_debug

Scope: `any`  
Target: `any`

```text
returns true if game is in debug mode (launched with -debug argument)
```

## is_decrypting

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if is currently decrypting a cipher. Example is_decrypting = GER
```

## is_defender

Scope: `COMBATANT`  
Target: `none`

```text
check if defender side in combat
```

## is_demilitarized_zone

Scope: `STATE`  
Target: `any`

```text
checks if a state is a demilitarized zone
```

## is_deployed

Scope: `CHARACTER`  
Target: `none`

```text
![MD]
Checks whether the scoped general's headquarters (HQ) is physically deployed on the map.

### Examples
''' 
my_character = {
	is_deployed = yes
}
''' 

```

## is_dynamic_country

Scope: `COUNTRY`  
Target: `any`

```text
returns true if the country is a dynamic country (tag is D01-D50)
```

## is_embargoed_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if embargoed by specified country
```

## is_embargoing

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if country is embargoing specified country
```

## is_exile_host

Scope: `COUNTRY`  
Target: `any`

```text
Checks if scope country is hosting an exile. is_exile_host = yes
```

## is_exiled_in

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if scope country is a government in exile in target tag. is_exiled_in = ENG
```

## is_exiled_leader

Scope: `CHARACTER`  
Target: `none`

```text
Checks if scope leader is from an exiled government. is_exiled_leader = yes
```

## is_exiled_leader_from

Scope: `CHARACTER`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if scope leader is from specified exiled government. is_exiled_leader_from = FRA
```

## is_faction_leader

Scope: `COUNTRY`  
Target: `none`

```text
check if country leads a faction
```

## is_female

Scope: `COUNTRY, CHARACTER, ACE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if scoped unit leader, ace or country is female
```

## is_field_marshal

Scope: `CHARACTER`  
Target: `none`

```text
is_field_marshal = yes/no - Checks if the current unit leader is a field marshall
```

## is_fighting_air_units

Scope: `COMBATANT`  
Target: `none`

```text
check if side is fighting air units
```

## is_fighting_in_strategic_region

Scope: `COMBATANT`  
Target: `none`

```text
![MD]
Checks whether the combat is taking place in the given strategic (naval) region, by id. Combatant scope.

### Example
''' 
# true if the battle is happening in strategic region 50
is_fighting_in_strategic_region = 50
''' 

```

## is_fighting_in_terrain

Scope: `COMBATANT`  
Target: `none`

```text
check what terrain is in combat
```

## is_fighting_in_weather

Scope: `COMBATANT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks the weather on a combat
Example:
# true if weather is artic water
is_fighting_in_weather = artic_water
# true if weather is either artic_water or snow
is_fighting_in_weather = { artic_water snow }

```

## is_fully_controlled_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if state is fully controlled by specified tag
```

## is_fully_decrypted

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks if fully decrypted a cipher. Example is_fully_decrypted = GER
```

## is_general_captured

Scope: `CHARACTER`  
Target: `none`

```text
![MD]
Checks if the scoped unit leader (general) is captured (by any country)

### Examples
''' 
my_character = {
	is_general_captured = yes
}
''' 

```

## is_government_in_exile

Scope: `COUNTRY`  
Target: `any`

```text
Checks if scope country an exiled government. is_government_in_exile = yes
```

## is_guaranteed_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if guaranteed by specified country
```

## is_high_command

Scope: `CHARACTER`  
Target: `none`

```text
_is_high_command_ = yes/no - Checks if the character in scope is hired as high command
```

## is_hired_as_advisor

Scope: `CHARACTER`  
Target: `none`

```text
is_hired_as_advisor = yes/no - Checks if the current character has at least one advisor role for which they are hired
```

## is_historical_focus_on

Scope: `any`  
Target: `none`

```text
check if the historical focus is active
```

## is_hosting_exile

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if scope country is hosting target tag as an exile. is_hosting_exile = FRA
```

## is_in_array

Scope: `any`  
Target: `none`

```text
Checks if an element is in array
Example: is_in_array = {
	array = array_name
	value = 42
}
#shorter usage: is_in_array = { array_name = 42 }
```

## is_in_faction

Scope: `COUNTRY`  
Target: `none`

```text
check if member of any faction
```

## is_in_faction_with

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if member of same faction as specified country
```

## is_in_home_area

Scope: `STATE`  
Target: `any`

```text
Checks if the first province in the state is connected to the capital of its owner
```

## is_in_peace_conference

Scope: `COUNTRY`  
Target: `none`

```text
Checks if the country is currently in a peaceconference
```

## is_in_state

Scope: `CHARACTER`  
Target: `THIS, ROOT, PREV, FROM, CAPITAL`

```text
![MD]
Checks if the character is in a specific state.
Works for deployed generals (HQ location), scientists (facility location including faction programs), and operatives (mission location).

### Example
''' 
# Check if a general is in a specific state
any_unit_leader = {
	is_in_state = 64 # Brandenburg
}

# Check if any scientist is in the capital
every_character = {
	limit = { is_active_scientist = yes }
	is_in_state = root.capital
}
''' 

```

## is_in_tech_sharing_group

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is member specified technology sharing group.
Example: is_in_technology_sharing_group = commonwealth_research
```

## is_ironman

Scope: `any`  
Target: `none`

```text
Check if current game is ironman.
```

## is_island_state

Scope: `STATE`  
Target: `any`

```text
"return true if the state is composed exclusively of one-province-islands.
More precisly, all provinces in the state have no land neighbor.
Or if they do they are connected by a strait.
(cf. is_one_state_island for checking if the state itself is an island)
ex: 145 = {
	is_island_state = yes
	is_island_state = no
}"
```

## is_justifying_wargoal_against

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country is justifying a wargoal against the target. 
Example: ENG = { is_justifying_wargoal_against = GER }
```

## is_leader_visible

Scope: `COUNTRY`  
Target: `any`

```text
Checks if the leader is visible to its owner (is_visible trigger in the leader's script)
```

## is_leading_army

Scope: `CHARACTER`  
Target: `none`

```text
is_leading_army = yes/no - Checks if the current unit leader is leading a single army (not army group)
```

## is_leading_army_group

Scope: `CHARACTER`  
Target: `none`

```text
is_leading_army_group = yes/no - Checks if the current unit leader is leading an army group (not single army)
```

## is_leading_army_in_province

Scope: `CHARACTER`  
Target: `none`

```text
is_leading_army_in_province = province_id # checks if the current unit leader is leading an army that has any division in a specific province. Block form { province = X include_field_marshal = yes } also counts a field marshal whose subordinate generals have a division in the province
```

## is_leading_volunteer_group

Scope: `CHARACTER, COMBATANT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is_leading_volunteer_group = FRA
```

## is_leading_volunteer_group_with_original_country

Scope: `CHARACTER, COMBATANT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is_leading_volunteer_group_with_original_country = FRA
```

## is_lend_leasing

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
is lend-leasing country
```

## is_licensing_any_to

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Current country is licensing something to target country
Example: is_licensing_any_to = ENG
```

## is_licensing_to

Scope: `COUNTRY`  
Target: `any`

```text
Country is licensing specific equipment to target. License is active
Example: is_licensing_to = {
	target = TAG # licensing to this country
	 #if archetype is specified equipment should not be specified
	archetype = light_tank_chassis #any light tank chassis license
	equipment = { # classical equipment reference
		type = light_tank_equipment_2
		version = 0 # optional: omit to match any version of the type
	}
}
```

## is_major

Scope: `COUNTRY`  
Target: `none`

```text
check if country is a major
```

## is_military_industrial_organization

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope matches the input token
ex:
var:my_mio_var = {
  is_military_industrial_organization = my_mio_token
}"
```

## is_mio_assigned_to_task

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope is assigned to at least 1 task.
ex:
mio:my_mio = {
	is_mio_assigned_to_task = yes
	is_mio_assigned_to_task = no
}"
```

## is_mio_available

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the available AND visible triggers in the Military Industrial Organisation in scope return true.
ex:
mio:my_mio = {
	is_mio_available = yes
	is_mio_available = no
}"
```

## is_mio_trait_available

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has a trait matching the input token, which is also available.
ex:
mio:my_mio = {
	is_mio_trait_available = my_trait_token
	is_mio_trait_available = {
		trait = my_trait_token
		check_mio_parent_completed = no # Optional, yes by default
        check_mio_mutually_exclusive = no # Optional, yes by default
	}
}"
```

## is_mio_trait_completed

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the Military Industrial Organisation in scope has a trait matching the input token, which is also completed.
ex:
mio:my_mio = {
	is_mio_trait_completed = my_trait_token
	is_mio_trait_completed = {
		trait = my_trait_token
	}
}"
```

## is_mio_visible

Scope: `INDUSTRIAL_ORG`  
Target: `none`

```text
"Checks if the visible trigger in the Military Industrial Organisation in scope returns true.
ex:
mio:my_mio = {
	is_mio_visible = yes
	is_mio_visible = no
}"
```

## is_navy_chief

Scope: `CHARACTER`  
Target: `none`

```text
_is_navy_chief_ = yes/no - Checks if the character in scope is hired as a navy chief
```

## is_navy_leader

Scope: `CHARACTER`  
Target: `none`

```text
is_navy_leader = yes/no - Checks if the current character is a navy leader
```

## is_neighbor_of

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if neighbor ( controlled territory ) with specified country
```

## is_on_continent

Scope: `STATE`  
Target: `none`

```text
is state located on continent
```

## is_on_same_continent_as

Scope: `STATE, COUNTRY`  
Target: `any`

```text
![MD]Checks if the scope state is on the same continent as the given state.
The capital state is used for given country tag.
Example 1:
''' 
FROM = {
	is_on_same_continent_as = 111
}
''' 
Example 2:
''' 
GER = {
	is_on_same_continent_as = ITA
}
''' 

```

## is_one_state_island

Scope: `STATE`  
Target: `any`

```text
"return true if the state is a one-state-island.
More precisely, all provinces in the state have no land neighbor.
Or if they do they are connected by a strait or the neighbor is inside the state.
ex: 145 = {
	is_one_state_island = yes
	is_one_state_island = no
}"
```

## is_operation_type

Scope: `OPERATION`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
checks the type of operation
```

## is_operative

Scope: `CHARACTER`  
Target: `none`

```text
is_operative = yes/no - Checks if the current character is an operative
```

## is_operative_captured

Scope: `CHARACTER`  
Target: `none`

```text
Checks whether the operative has the matching captured status

```

## is_owned_and_controlled_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if state is owned by
```

## is_owned_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if state is owned by
```

## is_owner_neighbor_of

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if neighbor ( owned territory ) with specified country
```

## is_political_advisor

Scope: `CHARACTER`  
Target: `none`

```text
is_political_advisor = yes/no - Checks if the character in scope is hired as a political advisor
```

## is_power_balance_in_range

Scope: `any`  
Target: `none`

```text
checks if current value power balance is within a certain range

Example:
is_power_balance_in_range = {
	id = power_balance_id
	range = power_balance_range_id
}
```

## is_power_balance_side_active

Scope: `any`  
Target: `none`

```text
checks if specified side is currently active

Example:
is_power_balance_side_active = {
	id = power_balance_id
	side = side_id
}
```

## is_preparing_operation

Scope: `COUNTRY`  
Target: `any`

```text
checks if preparing a specific operation.
Example: 
is_preparing_operation = { 
 target = ITA 
 operation = operation_infiltrate_armed_forces_navy}
```

## is_promoted_from_unit

Scope: `CHARACTER`  
Target: `none`

```text
"![MD]
Checks if a unit leader was promoted from a unit (division or ship).

### Example
''' 
any_unit_leader = {
	is_promoted_from_unit = yes
}
''' 
"
```

## is_puppet

Scope: `COUNTRY`  
Target: `any`

```text
Checks if the country is puppet of any other country
```

## is_puppet_of

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if the country is puppet of specified country
```

## is_researching_technology

Scope: `COUNTRY`  
Target: `none`

```text
Checks if the country is currently researching a specific technology.
Example: is_researching_technology = mechanised_infantry
```

## is_running_operation

Scope: `COUNTRY`  
Target: `any`

```text
checks if running a specific operation. operation can be ommitted to check for any operation
Example: 
is_running_operation = { 
 target = ITA 
 operation = operation_infiltrate_armed_forces_navy}
```

## is_scientist_injured

Scope: `CHARACTER`  
Target: `any`

```text
"Checks if the scientist of the character in scope is injured
is_scientist_injured = <bool>
ex: my_character = {
        is_scientist_active = yes
	}
"
```

## is_special_project_being_researched

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the country in scope is currently researching the special project in input.
ex:
SOV = {
	is_special_project_being_researched = sp:my_project
	is_special_project_being_researched = var:my_project_var
	is_special_project_being_researched = PREV # accepts variables and keywords
}"
```

## is_special_project_completed

Scope: `COUNTRY`  
Target: `none`

```text
"Checks if the country in scope has completed the special project in input.
ex:
SOV = {
	is_special_project_completed = sp:my_project
	is_special_project_completed = var:my_project_var
	is_special_project_completed = PREV # accepts variables and keywords
}"
```

## is_spymaster

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check if country is Spy Master
```

## is_staging_coup

Scope: `COUNTRY`  
Target: `none`

```text
is_staging_coup = yes - Returns true if current country is staging a coup in another any country.
```

## is_subject

Scope: `COUNTRY`  
Target: `any`

```text
Checks if the country is subject of any other country
```

## is_subject_of

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if the country is subject of specified country
```

## is_target_of_coup

Scope: `COUNTRY`  
Target: `none`

```text
is_target_of_coup = yes - Returns true if current country is being targeted by a coup from any country.
```

## is_theorist

Scope: `CHARACTER`  
Target: `none`

```text
is_theorist = yes/no - Checks if the character in scope is hired as a theorist
```

## is_tutorial

Scope: `any`  
Target: `none`

```text
check if the tutorial is active
```

## is_unit_leader

Scope: `CHARACTER`  
Target: `none`

```text
is_unit_leader = yes/no - Checks if the current character is a unit leader
```

## is_unit_template_reserves

Scope: ``  
Target: `any`

```text
returns true if this unit's template has the reserves priority
```

## is_winning

Scope: `COMBATANT`  
Target: `none`

```text
check if defender side in combat
```

## land_doctrine_level

Scope: `COUNTRY`  
Target: `none`

```text
checks researched land doctrine level
```

## less_combat_width_than_opponent

Scope: `COMBATANT`  
Target: `none`

```text
check if side has more combat width than their opponent
```

## log

Scope: `any`  
Target: `none`

```text
Print message to game.log - Can be localized
```

## logistics_skill_level

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
Compares logistics skill level of a unit leader.
Example: logistics_skill_level > 5
```

## longest_war_length

Scope: `COUNTRY`  
Target: `none`

```text
Check number of months the country has been at war
```

## manpower_per_military_factory

Scope: `COUNTRY`  
Target: `none`

```text
Number of available manpower per factory the country has. Excluding dockyards.
manpower_per_military_factory < 1000
```

## meta_trigger

Scope: `STATE, COUNTRY, CHARACTER, COMBATANT, ACE, STRATEGIC_REGION, OPERATION, INDUSTRIAL_ORG, PURCHASE_CONTRACT, RAID_INSTANCE, SPECIAL_PROJECT, FACTION`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
meta triggers can be used for building triggers from strings and running them. following example will test if Germany has 42 pp:
meta_trigger = {
    text = {
        [COUNTRY] = {
            political_power > [POW]
        }
    }
    COUNTRY = "GER"
    POW = 42
    debug = no #set to yes if you want to see what game actually executes
}

```

## min_planning

Scope: `COMBATANT`  
Target: `none`

```text
check if side has maximal planning bonus
```

## mine_threat

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
A trigger to check how dangerous enemy mines are for a country. Controlled by NAVAL_MINE_DANGER defines. Returns a value between 0 and 1. Example mine_threat > 0.5 
```

## modulo_temp_variable

Scope: `any`  
Target: `none`

```text
modulos a temp variable with another. Example: 
modulo_temp_variable = { 
  var = variable_to_modulo 
  value = divisior 
}
```

## multiply_temp_variable

Scope: `any`  
Target: `none`

```text
![MD]
Multiplies a temporary variable by a value, another variable, or a [math expression](script_math_expression.md).

### Examples
''' 
multiply_temp_variable = { num_dogs = 2 }
multiply_temp_variable = {
	num_dogs = { value = num_cats  add = 1 }
}
''' 

```

## naval_strength_comparison

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares navies of two sides.
naval_strength_comparison = {
	other = GER # by default compares to the from scope
  tooltip = 'key' #tooltip is 'navy strength' by default, the key can be overridden if wanted 
	ratio > 1.5   # default is 1
	sub_unit_def_weights = { # if not specified, it will weigh all ships as 1. otherwise only specified sub unit types will be counted
		carrier = 1
		battleship = 2
	}
}

```

## naval_strength_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the estimated navy strength between the scope country and the one set with 'tag' 
naval_strength_ratio = { 
  tag = GER 
  ratio > 0.5 
}
```

## network_national_coverage

Scope: `COUNTRY`  
Target: `none`

```text
checks network national coverage you have over a country. Example: 
network_national_coverage = { 
 target = GER
 value > 0.5
} 

```

## network_strength

Scope: `COUNTRY`  
Target: `none`

```text
checks network strength you have in a country. Examples: 
# country has a network strength greater than 50% over germany
network_strength = { 
 target = GER
 value > 50
}

# country has a network strength greater than 50% over germany in state 53
network_strength = { 
 target = GER
 state = 53 value > 50
}

# country has a network strength greater than 50% in state 53, regardless of the target
network_strength = { 
 state = 53
 value > 50
}


```

## night

Scope: `COMBATANT`  
Target: `none`

```text
check if combat is at night
```

## non_damaged_building_level

Scope: `STATE`  
Target: `none`

```text
check if a state has enough non damaged buildings


Example:
non_damaged_building_level = {
	building = arms_factory
	level = 5
}
```

## not

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
negates content of trigger
```

## not_already_hired_except_as

Scope: `CHARACTER`  
Target: `none`

```text
not_already_hired_except_as = <slot> - For characters with several advisor roles, checks if the current character is already assigned in another advisor slot.
example: let's say a character can be a political advisor and a theorist. But they should only be hired in one role, never both at the same time.
then you may set in the advisor available trigger :
	advisor = {
		slot = political_advisor
		available = { not_already_hired_except_as = political_advisor } 
		...
	}
	advisor = {
		slot = theorist
		available = { not_already_hired_except_as = theorist } 
		...
	}

```

## num_battalions_in_states

Scope: `COUNTRY`  
Target: `any`

```text
Checks number of battalions in states (optionally filtering on battalion types). Using a custom tooltip is highly recommended since the default tooltip leaves out some information for the sake of readability.
Example:
num_battalions_in_states = {
	count > 5 (or <, =)
	states = { 550 559 }
	types = { infantry cavalry } [optional - will count all except excluded if not specified]
	exclude = { light_armor } [optional - will count all (included) if not specified]
}
```

## num_divisions

Scope: `COUNTRY`  
Target: `none`

```text
Will compare towards the amount of divisions a country has control over, if strength matters use has_army_size.
```

## num_divisions_in_states

Scope: `COUNTRY`  
Target: `any`

```text
Checks number of divisions in states (optionally filtering on majority division types). Using a custom tooltip is highly recommended since the default tooltip leaves out some information for the sake of readability.
Example:
num_divisions_in_states = {
	count > 5 (or <, =)
	states = { 550 559 }
	types = { infantry cavalry } [optional - will count all except excluded if not specified]
	exclude = { light_armor } [optional - will count all (included) if not specified]
}
```

## num_faction_members

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the number of members in the faction for the current country. 
 Example: num_faction_members > 10
```

## num_fake_intel_divisions

Scope: `COUNTRY`  
Target: `none`

```text
Will compare towards the amount of fake intel divisions a country has control over. .
```

## num_finished_operations

Scope: `COUNTRY`  
Target: `any`

```text
Compares number of completed operations.
Example: 
num_finished_operations = { 
 target = ITA 
 operation = operation_infiltrate_armed_forces_navy value > 35 
}
```

## num_free_operative_slots

Scope: `COUNTRY`  
Target: `none`

```text
Checks the number of operative a country can recruit right now.
Note that this is not necessarily greater than zero if num_operative_slots returned a number greater than the number of operative.
```

## num_nukes_being_dropped

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
total number of nukes that are currently ready to be dropped
```

## num_nukes_left_to_drop

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
number of nukes left to drop during this game tick (only useful in-between nuke drops, like in on_nuke_drop on-action, for example)
```

## num_occupied_states

Scope: `COUNTRY`  
Target: `none`

```text
check the number of states occupied by nation
```

## num_of_available_civilian_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of available civilian factories
```

## num_of_available_military_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of available military factories
```

## num_of_available_naval_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of available naval factories
```

## num_of_career_profile_points

Scope: `any`  
Target: `any`

```text
check amount of gained career points
```

## num_of_civilian_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of civilian factories
```

## num_of_civilian_factories_available_for_projects

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of civilian factories available for a new project to use
```

## num_of_controlled_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check the number of factories in controlled states excluding any gained or lost through trade, relations, modifiers etc.
```

## num_of_controlled_states

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of controlled stats
```

## num_of_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check amount of available factories (excluding temporary sources like trade and lend-lease)
Example:
GER = { num_of_factories < 50 }
```

## num_of_military_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of military factories
```

## num_of_naval_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of naval factories
```

## num_of_nukes

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of nukes
```

## num_of_operatives

Scope: `COUNTRY`  
Target: `none`

```text
Checks the number of operatives the country controls
```

## num_of_owned_factories

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check the number of factories in owned states excluding any gained or lost through trade, relations, modifiers etc.
```

## num_of_supply_nodes

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of supply nodes
```

## num_operative_slots

Scope: `COUNTRY`  
Target: `none`

```text
Checks the number of available operative slots a country has.
If this differs from the number of operative, this does not mean the country can recruit an operative, but that it will eventually be able to.
```

## num_owned_neighbour_states

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if a country owns the amount of states neighbouring the scoped state
```

## num_planes_stationed_in_regions

Scope: `COUNTRY`  
Target: `none`

```text
Will compare the number of planes which have bases in the specified regions. Supports < > =
Example: num_planes_stationed_in_regions = {
value < 100
regions = { 18 47 }
}
```

## num_researched_technologies

Scope: `COUNTRY`  
Target: `none`

```text
Number of researched technologies
```

## num_subjects

Scope: `COUNTRY`  
Target: `none`

```text
check the number of subjects of nation
```

## num_tech_sharing_groups

Scope: `COUNTRY`  
Target: `none`

```text
checks how many groups a nation is a member of
```

## num_units

Scope: `CHARACTER`  
Target: `none`

```text
Check number of units commanded by the unit leader 
 num_units > 2
```

## occupation_law

Scope: `STATE, COUNTRY`  
Target: `any`

```text
"Checks the occupation law for an occupied country, occupied state, or the default occupation law of an occupying country.

- If THIS is a country and it's the same as the PREV country, then THIS's default law is checked.
- If THIS is a country and it's different from the PREV country, then PREV's country law for THIS is checked.
- If THIS is a state, then the occupier's state law is checked.

Example:
GER = { occupation_law = autonomous_occupation }
GER = { POL = { occupation_law = foreign_civilian_oversight } }
123 = { occupation_law = local_police_force_garrison }"
```

## occupied_country_tag

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
compares occupied country that creates resistance to a tag. Example: occupied_country_tag = ITA
```

## operative_leader_mission

Scope: `CHARACTER`  
Target: `none`

```text
Checks whether the operative is performing the given mission:
operative_leader_mission = build_intel_network
```

## operative_leader_operation

Scope: `CHARACTER`  
Target: `none`

```text
Checks whether the operative is performing the given operation:
operative_leader_operation = operation_rescue_operative
```

## or

Scope: `any`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
at least one entry inside trigger must be true
```

## original_research_slots

Scope: `COUNTRY`  
Target: `none`

```text
check number of research slots at start of game
```

## original_tag

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
original tag is ( for civil wars checks )
```

## owns_any_state_of

Scope: `COUNTRY`  
Target: `none`

```text
Check if the country owns any of the states in the list.
```

## owns_state

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, CAPITAL`

```text
check owner for state(s)
```

## pc_current_score

Scope: `COUNTRY`  
Target: `none`

```text
Checks country's total peace conference score. Only usable if the country is on the winning side.
Example:
CZE = { pc_current_score > 400 }
```

## pc_does_state_stack_demilitarized

Scope: `STATE`  
Target: `none`

```text
Checks if state got demilitarized stacked on it in the peace conference.
Example:
FROM.FROM.FROM = { pc_does_state_stack_demilitarized = yes }
```

## pc_does_state_stack_dismantled

Scope: `STATE`  
Target: `none`

```text
Checks if state got dismantled stacked on it in the peace conference.
Example:
FROM.FROM.FROM = { pc_does_state_stack_dismantled = yes }
```

## pc_is_forced_government

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has had their government force-changed in the peace conference.
Example:
CZE = { pc_is_forced_government = yes }
```

## pc_is_forced_government_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country has had their government force-changed by a certain country in the peace conference.
Example:
CZE = { pc_is_forced_government_by = GER }
```

## pc_is_forced_government_to

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has had their government force-changed to a certain ideology in the peace conference.
Example:
CZE = { pc_is_forced_government_to = communism }
```

## pc_is_liberated

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country has been liberated in the peace conference.
Example:
CZE = { pc_is_liberated = yes }
```

## pc_is_loser

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is a loser in the peace conference.
Example:
ENG = { pc_is_loser = yes }
```

## pc_is_on_same_side_as

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country is on same side (winning or losing side) as another country in the peace conference.
Example:
POL = { pc_is_on_same_side_as = ENG }
```

## pc_is_on_winning_side

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is on the winning side in the peace conference.
Example:
CZE = { pc_is_on_winning_side = yes }
```

## pc_is_puppeted

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is a puppet, or has been released as a puppet in the peace conference.
Example:
CZE = { pc_is_puppeted = yes }
```

## pc_is_puppeted_by

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks if country is a puppet of a certain country, or has been released as a puppet by a certain country in the peace conference.
Example:
CZE = { pc_is_puppeted_by = GER }
```

## pc_is_state_claimed

Scope: `STATE`  
Target: `none`

```text
Check if state is claimed (and uncontested) in conferenceExample:
pc_is_state_claimed = yes/no
```

## pc_is_state_claimed_and_taken_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if state is claimed with a take_states action in conference for TAG
Example:
pc_is_state_claimed_and_taken_by = SOV/ROOT/ROOT.FROM
```

## pc_is_state_claimed_by

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if state is claimed in conference by TAG
Example:
pc_is_state_claimed_by = SOV/ROOT/ROOT.FROM
```

## pc_is_state_outside_influence_for_winner

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check if state is outside valid influence range for winner TAG in the current peace conference
Example:
pc_is_state_outside_influence_for_winner = SOV/ROOT/ROOT.FROM
```

## pc_is_winner

Scope: `COUNTRY`  
Target: `none`

```text
Checks if country is a winner in the peace conference.
Example:
ENG = { pc_is_winner = yes }
```

## pc_total_score

Scope: `COUNTRY`  
Target: `none`

```text
Checks country's total peace conference score. Only usable if the country is on the winning side.
Example:
CZE = { pc_total_score > 400 }
```

## pc_turn

Scope: `any`  
Target: `none`

```text
Checks turn number in PC.
Example:
pc_turn > 20
```

## phase

Scope: `COMBATANT`  
Target: `none`

```text
check if we are in this combat phase
```

## planning_skill_level

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
Compares planning skill level of a unit leader.
Example: planning_skill_level > 5
```

## political_power_daily

Scope: `COUNTRY`  
Target: `none`

```text
Checks if daily political power increase is more or less that specified value 
 political_power_daily > 1.5
```

## political_power_growth

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check the value of political power daily growth.Exacmple: political_power_growth > 0
```

## power_balance_daily_change

Scope: `any`  
Target: `none`

```text
compares current total daily change of a power balance

Example:
power_balance_daily_change = {
	id = power_balance_id
	value > 0.5 # supported operators are: >, < and =
}
```

## power_balance_value

Scope: `any`  
Target: `none`

```text
compares current value of a power balance

Example:
power_balance_value = {
	id = power_balance_id
	value > 0.5 # supported operators are: >, < and =
}
```

## power_balance_weekly_change

Scope: `any`  
Target: `none`

```text
compares current total weekly change of a power balance

Example:
power_balance_weekly_change = {
	id = power_balance_id
	value > 0.5 # supported operators are: >, < and =
}
```

## print_variables

Scope: `any`  
Target: `none`

```text
prints all variables in scope and temp variables to a file
Example: print_variables = {
file = log_file
text = header_text
append = yes
print_global = yes
var_list = { a b c } #optional
}
```

## province_vp

Scope: `COMBATANT`  
Target: `none`

```text
"Check if the victory points of the combatants province is larger or less than the provinded amount.
For example:
province_vp > 2
province_vp < 3"
```

## received_expeditionary_forces

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Checks that the country in scope has received the specified amount of expeditionary forces from the specified country
E.g. true if Germany is commaning more than 100 expeditionary forces from Poland:
GER = {
  received_expeditionary_forces = {
    sender = POL
    value > 100
  }
}
```

## recon_advantage

Scope: `COMBATANT`  
Target: `none`

```text
checks if side has an advantage in recon level
```

## region

Scope: `STATE`  
Target: `none`

```text
check state's strategic area id
```

## remove_from_temp_array

Scope: `any`  
Target: `none`

```text
Removes an element from a temporary array using value or index
Example: remove_from_temp_array = {
	array = array_name
	value = 42 #optional, use index or this. if neither it removes last element
	index = 3 #optional, use value or this. if neither it removes last element
}
#shorter usage: remove_from_temp_array = { array_name = 42 }
```

## reserves

Scope: `COMBATANT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
check amount of reserves
```

## resistance

Scope: `STATE`  
Target: `any`

```text
Compares the current resistance level of a state to a value. Example: resistance > 50 
```

## resistance_speed

Scope: `STATE`  
Target: `any`

```text
Compares the current resistance speed of a state to a value. Example: resistance_speed > 50 
```

## resistance_target

Scope: `STATE`  
Target: `any`

```text
Compares the target resistance level of a state to a value. Example: resistance_target > 50 
```

## resize_temp_array

Scope: `any`  
Target: `none`

```text
Resizes a temp array
Example: resize_temp_array = {
	array = array_name
	value = 42 #optional, if not specified and array grows the new elements are set to this (default 0)
	size = 3 #if higher than old size, new elements are added to end. otherwise last elements are removed to match to new size
}
#shorter usage: resize_temp_array = { array_name = 3 }
```

## resource_count_trigger

Scope: `STATE, COUNTRY`  
Target: `none`

```text
Checks if the current scope has the specified amount of the specified resource.
Usage: <Resource> < <int>
Supported Resources: oil, aluminium, rubber, tungsten, steel, chromium, coal.
```

## round_temp_variable

Scope: `any`  
Target: `none`

```text
Rounds a temporary variable
Example: round_temp_variable = num_dogs
```

## scope_exists

Scope: `any`  
Target: `none`

```text
"Check if the current scope exist.
This differ from for example exists that checks if the country of the scope exists.
This checks if the scope for the country exists and the other if the country itself exists in the game.
Note that variable scopes are always valid scopes.
Example:
DEN = { exists = yes } # Should always be true since DEN is always a valid scope
sp:sp_land_flamethrower_tank = {
	character = {
		scope_exists = yes
	}
} # True if the project has an assigned scientist.
var:my_var = {
	scope_exists = yes # Always true since variables are always valid scopes
}
"
```

## seller

Scope: `PURCHASE_CONTRACT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check the seller country. Example: seller = GER
```

## set_temp_variable

Scope: `any`  
Target: `none`

```text
![MD]
Sets a temporary variable to a value, another variable, or a [math expression](script_math_expression.md).

### Examples
''' 
set_temp_variable = { num_dogs = 42 }
set_temp_variable = {
	var = num_dogs
	value = 42
	tooltip = loc_str_id_with_LEFT_and_RIGHT
}
set_temp_variable = {
	num_dogs = { value = num_cats  multiply = 2  add = 1 }
}
''' 

```

## set_temp_variable_to_random

Scope: `any`  
Target: `none`

```text
sets a temp variable to a random value. example 
set_temp_variable_to_random = num_dogs #sets num_dogs a random value between [0, 1) 
set_temp_variable_to_random = { 
	var = num_dogs #variable to set 
	min = 5 #default 0. value will be set in between [min, max) 
	max = 10 #default 1. value will be set in between [min, max) 
	integer = yes #default no. if yes the number value will be an integer 
} 

```

## ships_in_area

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of ships in specified area
```

## ships_in_state_ports

Scope: `COUNTRY`  
Target: `none`

```text
checks for amount of ships in specified state's ports. 
ships_in_state_ports = { 
  type = ship_category 
  state = state_id (or scopped variable) 
  size = 42 
}
```

## skill

Scope: `CHARACTER, COMBATANT`  
Target: `none`

```text
compare leader skill levels
```

## skill_advantage

Scope: `COMBATANT`  
Target: `none`

```text
compare leader skill levels
```

## state

Scope: `STATE`  
Target: `THIS, ROOT, PREV, FROM, CAPITAL`

```text
check state id
```

## state_and_terrain_strategic_value

Scope: `STATE`  
Target: `none`

```text
Checks for state strategic value
```

## state_population

Scope: `STATE`  
Target: `none`

```text
check the population in the state
```

## state_population_k

Scope: `STATE`  
Target: `none`

```text
check the population in the state in thousands (use to avoid variable overflows)
```

## state_strategic_value

Scope: `STATE`  
Target: `none`

```text
Checks for state strategic value
```

## stockpile_ratio

Scope: `COUNTRY`  
Target: `none`

```text
Compares the ratio of equipment archetype in stockpile vs used. a value of 2 means we have double in stockpile of what is fielded or in training.
```

## strength_ratio

Scope: `COUNTRY`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Compares the estimated army strength between the scope country and the one set with 'tag'
```

## subtract_from_temp_variable

Scope: `any`  
Target: `none`

```text
![MD]
Subtracts a value, a variable, or a [math expression](script_math_expression.md) from a temporary variable.

### Examples
''' 
subtract_from_temp_variable = { num_dogs = 5 }
subtract_from_temp_variable = {
	num_dogs = { value = num_cats  multiply = 2 }
}
''' 

```

## surrender_progress

Scope: `COUNTRY`  
Target: `none`

```text
check if a country is close to surrendering
```

## tag

Scope: `COUNTRY, CHARACTER, COMBATANT`  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
country tag trigger
```

## target_conscription_amount

Scope: `COUNTRY`  
Target: `none`

```text
Checks the target conscription amount of the country.

```

## temperature

Scope: `COMBATANT`  
Target: `none`

```text
check combat province temperature
```

## threat

Scope: `any`  
Target: `none`

```text
check the global threat value (world tension). 0-1 value
```

## unit_organization

Scope: ``  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check scope unit organization status 0-1: Example unit_organization < 1
```

## unit_strength

Scope: ``  
Target: `THIS, ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL`

```text
Check scope unit strength status 0-1: Example unit_strength < 1
```

## war_length_with

Scope: `COUNTRY`  
Target: `none`

```text
Check number of months the country has been at war with X for Y months.
 war_length_with = { tag = X months > Y }
```

