# 进阶脚本概念与格式参考

来源：[CWTools HOI4 配置固定提交](https://github.com/cwtools/cwtools-hoi4-config/tree/297dd69c42aabe10078a8b7ab7f2d07ee631d4ef)。

上游版权：Copyright (c) 2018 tboby；适用 [MIT 许可](../cwtools-hoi4-config/LICENSE)。本文件由上游 `Config/script_documentation.json` 重新排版生成，未独立验证引擎行为。快照取得日期：2026-10-24；其对应的精确游戏版本未知。条目数量不代表引擎接口总量。

描述中的数值、示例和作用域均来自上游，可能存在遗漏或错误；实际开发须以目标游戏版本文档和运行结果复核。

## script_concepts

### Math Expressions


Math expressions allow for mathematical calculations using constants, scoped variables and mathematical functions.
Using math expressions is expected to be more performant than using temporary variables for calculations.

All math expressions are based on fixed point arithmetic. For boolean operations, 0.0 is considered false and any
other value is considered true. All operators that return a boolean value will return 1.0 for true and 0.0 for false.

A list of math functions can be found [here](script_math_functions.md).

### Syntax
Math expressions use a base value (`value = ...`) that is then modified by sequential statements.
Statements can either be:
* No argument statement (e.g. `round = yes`) that simply applies an operation to the accumulator.
* Simple statements that takes one or more math expression as argument (e.g. `add = 5`, `clamp = { min = 0 max = 100 }`).
* Control flow statements that take a block of statements as argument (e.g. `if = { limit = { value = x  greater_than = 10 }  add = 100 }`).
* Collection iterators that takes a named collection and a block of modification statements to apply for each element. The collection elements will be scoped to.

### Error Handling
If a math expression fails to parse properly, it will be replaced with the value 0.0 for runtime operations.

### Examples
```
{ value = num_cavalry
  add = num_motorized
  add = num_mechanized
  greater_than = { value = num_units  multiply = 0.4 }
}
```

### Bindable Localization

![MD]
Bindable localization is a modular way of binding localization parameters in script for the specified localization key.
Any variable that accepts a bindable localization accepts the following:
* A [formatted localization](#formatted-localization).
* A bound localization object.

The bound localization object has the following members:
* `localization_key = KEY`: The localization key that is used for the object.
* `PARAMETER = BINDABLE_LOC`: A parameter to the localization key that is replaced with the localized version `BINDABLE_LOC`,
   where `BINDABLE_LOC` is a bound localization object itself.

#### Examples
The following are example usages where the `tooltip` is a bindable localization:
```
tooltip = MY_TOOLTIP # Simple loc key tooltip

### Loc entries
MY_TOOLTIP = "This is a tooltip"

### Localized result
This is a tooltip
```

```
tooltip = {
	localization_key = MY_TOOLTIP # Root look key
	IMPORTANT_QUESTION = { # ID IMPORTANT_QUESTION in MY_TOOLTIP will get value:
		localization_key = MEANING_OF_LIFE # Root loc key in IMPORTANT_QUESTION
		ANSWER = "42" # ID ANSWER in IMPORTANT_QUESTION will get value 42
	}
	THE_REST_IS = UNIMPORTANT
}

### Loc entries
MY_TOOLTIP = "The thing everyone wonders is if $IMPORTANT_QUESTION$. The rest is $THE_REST_IS$."
MEANING_OF_LIFE = "the meaning of life is $ANSWER$"
UNIMPORTANT = "unimportant"

### Result
The thing everyone wonders is if the meaning of life is 42. The rest is unimportant.
```

```
# Using a formatter
custom_effect_tooltip = idea_desc|canadian_pacific_railway
```


### Formatted Localization

![MD]
Formatted localization is a concept for generating texts based on a specific token. It can for example, be used to
generate a description of an idea from the ideas token. A formatted localization entry also accepts standard localization keys
and raw localization strings giving the following allowed options:
* A localization tag.
* A string (can for example be used to inject things based on the Localization Scope Object if one exists).
* A formatter and it's associated tag.

Documentation for the existing formatters can be found at [Localization formatter](localization_formatter.md).

### Example
```
# Using a  formatter
custom_effect_tooltip = idea_desc|canadian_pacific_railway

# Using a standard loc key
custom_effect_tooltip = WHILE_FOCUSING

# Using a loc string with a localization scope object
custom_effect_tooltip = "[ROOT.GetName]"
```


### Collections

![MD]
Collections are a collection of game objects of the same type, just like the game arrays.
However, unlike arrays they support operations to transform, expand or filter the original
collection in a unified and efficient way. In many cases, using arrays in combinations with
triggers can achieve the same results as collections. However, in quite a few of them, collections
are expected to be more efficient and easier to script. For example, checking that the number of
owned states within the faction is larger than 42 would require doing an implicit loop over all faction members
(using an all of trigger) and adding the number of owned states to a temporary variable.
Finally, that variable would be compared to whatever value is needed. To make it clear to the
player that probably needs a custom tooltip as well. With collections, you could achieve the
same result with a single trigger:
```
collection_size = {
	input = {
		input = game:scope
		operators = { faction_members owned_states }
		name = "States owned by any faction member"
	}
	value > 42
}
```

### Collection structure
A collection contains three properties `input`, `operators` and `name`.
Where both `operators` and `name` are optional.
- `input` is the original set of item to use as the base of the collection.
  All available inputs can be found in their [documentation](script_collection_input.md).
- `operators` are all the operations that can be applied to the collection in order.
  To generate the desired set of game items. All operators are documented [here](script_collection_operator.md).
- `name` is the name of the collection. It is used to describe the collection where it is used.

A collection is built from the `input` and the `operators` by going through all the items
in the input and apply all the operators to that item in order. So in the example of the
owned states within the faction, the collections input is the current scope (which we
assume is a country). So for each country in the scope (one), the `faction_members
operator is applied, that yields all the members of the faction (including the country itself).
Now for every country in the faction, the operator `owned_states` is applied.
This generates a set of states owned by the faction members.

### Shorthand notations
There is currently one shorthand notation for collections: Using only input. This allows you only provide
the input to the collection instead of the complete object. For example, the following collections are equivalent:
```
my_collection = {
	input = game:all_states
}

my_collection = game:all_states
```

### Uniqueness of game items
There is one pitfall that should be noted, there is no guarantee that the objects in
the collection is unique. So if we for example replace the `owned_states` operator with
a `core_states` operator, the collection will contain the same state multiple times if
multiple faction members has core of the same state.

### Named collections
A named collection is a collection that is defined in the collections database. It has a unique name
and can be used as input in other collections. For more information see the [input documentation](script_collection_input.md).

### Localization of collections
A collection is localized using the `name` property. If the collection has no name, it will use the name of the input
collection.


### Script Constants

![MD]
Script constants are a way to define constants in scripts that can be reused in any script file (except for other script constants files).
In general, script constants can be used instead of the script macro operator `@` that is file local.
Note that the script constants has a negligible load time impact and no runtime performance cost.
Like many other concepts, the script constant is only supported where explicitly stated that it is supported. However, all scoped variables
accepts script constants that are pointing to a single fixed point value, by using the prefix `constant:`.

#### Reloading
A script constant is a bit specific when it comes to reloading the database.
It's not enough to reload the script constant database itself since script constants are injected into the script on load.
Instead one have to first reload the script constant database, and then reload the database that uses the script constant.

#### Example
In the script constant file, the following constant file definition is made:
```
numeric_constants = {
    schema = {
        any_key = yes
        data = fixed_point # floating point
    }
	pi = 3.14159
	e = 2.71828
}
```

These can then be used in a script file like this:
```
some_scoped_variable = constant:numeric_constants.pi
some_fixed_point_supporting_constants = numeric_constants.e
```



### Contextual Localization

![MD]
Contextual localization is a way to access data from Localization Objects when localizing a string.
The concept differs slightly from standard values ($VAL$) that can be injected into the localization string by allowing the localization string
to select which properties to add to the resulting string and where.
When a string is contextually localized with a localization object, then there's one root object (either a [Scope](loc_objects_documentation.md#scope) or [Localization Environment](loc_objects_documentation.md#localization-environment).
In general this object can only be used for two purposes: Accessing other objects and getting the current date.

The documentation for the different localization objects can be found at [Localization Objects](loc_objects_documentation.md).

### Using a localization object
The localization objects are used with the following syntax: `[(Object.)+Property]`.
`(Object.)+` refers to a sequence of at least one object accessor and `Property` is the property
that is accessed by the last object in the sequence. For example, if the localization string is localized with an [Character](loc_objects_documentation.md#character) object
the following queries would get the character's name and the name of the country that the character belongs to `[Character.GetName]`
and `[Character.Owner.GetName]`, respectively.

### Condition in contextual localization
Conditions in contextual localization can be used to check if objects are null or not. The basic syntax for the condition is `[(OBJECT ? TRUE_CASE : FALSE_CASE)]`.
Where:
* `OBJECT` is any object you can use to access a property from (for example, `Character` and `Character.Owner` are valid objects).
* `TRUE_CASE` and `FALSE_CASE` are what is to be localized if `OBJECT` is not null and null, respectively. These can hold one of the following values:
   1. `'LOC_KEY` - A localization key (`LOC_KEY`, note the prepending `'` that means that it's a localization key) that will be localized using the same context as the root contextual localization.
   2. `(OBJECT.)+Property` - Standard access of a property from an object (discards the object before the `?`). `(OBJECT.)+` stands for a sequence of at least one object, with dots as separators.
   3. (true case only) `.(OBJECT.)*Property` - Continue that object sequence from the object before the `?`. `(OBJECT.)*` stands for a potentially empty sequence of objects with dots as separators. This is more efficient than the second option since it will not redo the object getters before the `?`.

### Relation to Event Scopes
When a localization string is localized from a scoped context (for example effects or triggers), then the root [Scope](loc_objects_documentation.md#scope) is created
from the event scope of that context. For example, an effect that creates a trade route between two countries `FROM` and `THIS`
could be localized with: `LOC_KEY: "Creates a trade route between [FROM.GetName] and [THIS.GetName]"`. For more information on
how the scope accessors `FROM`, `THIS`, `PREV` and `ROOT` works on `Scope` see TODO: Add link.

### Documentation of localized objects
In general a scoped context (for example, effects and triggers) are localized using a [Scope](loc_objects_documentation.md#scope) object based on the scope of that context.
However, there are legacy systems where this may not hold. For other places where localization keys are provided, please see the documentation
for which localization objects that are defined for that context.

## loc_formatter

### country_culture

![MD]
The country_culture formatter formats the string using the country's cultural override (`TAG_token`) if it exists,
otherwise the generic version (`token`).

### Localization Scope Object
The formatter requires the following Localization Scope Objets to be defined:
* `Country` - The country that the idea is associated with.

### Example
```
custom_effect_tooltip = country_culture|generic_tank_organisation
```


### country_leader_desc

![MD]
The country_leader_desc formatter gets the description for a possible country leader.

### Localization Scope Object
No scope needed - This formatter searches in the database for the character with given ideology.

### Parameters
The formatter supports two additional parameters, INDENT and IDEOLOGY
- IDEOLOGY: (Mandatory) Select the characters ideology leader role to use, use the ideology group token prefixed with 'token:'.
- INDENT: (Optional) The indent to be added to all lines of the country leader trait description (including header line).

### Example
```
custom_effect_tooltip = country_leader_desc|hjalmar_schacht

custom_effect_tooltip = {
	localization_key = country_leader_desc|hjalmar_schacht
	IDEOLOGY = token:fascism
	INDENT = 2_SPACES
```


### building_state_modifier

![MD]
The building_state_modifier gets the state modifiers for the provided building template and the provided scope.

The formatter takes special care of the following parameters:
- INDENT: The indent to be added to all lines of the state modifier description (including header line).

### Example:
```
custom_effect_tooltip = building_state_modifier|dam
```


### advisor_desc

![MD]
The advisor_desc formatter gets the description for the advisor.

### Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:
* `Country` - The country that the idea is associated with.

### Example
```
custom_effect_tooltip = advisor_desc|hjalmar_schacht
```


### tech_effect

![MD]
The tech_effect formatter gets the effect of finishing a technology.

### Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:
* `Country` - The country that the tech is associated with.

### Example
```
custom_effect_tooltip = tech_effect|early_transport_plane
```


### idea_desc

![MD]
The idea_desc formatter gets the description for the idea.

### Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:
* `Country` - The country that the idea is associated with.

### Example
```
custom_effect_tooltip = idea_desc|canadian_pacific_railway
```


### idea_name

![MD]
The idea_name formatter formats gets the name for the idea.

### Localization Scope Object
The formatter requires the following Localization Scope Objects to be defined:
* `Country` - The country that the idea is associated with.

### Example
```
custom_effect_tooltip = idea_name|canadian_pacific_railway
```


### equipment_directories_that_can_use_module

![MD]
The equipment_directories_that_can_use_module gets a list of the different directories (e.g. tank, ship, planes)).

The formatter takes special care of the following parameters:
- INDENT: The indent to be added to all lines of the state modifier description (including header line).

### Example:
```
custom_effect_tooltip = equipment_directories_that_can_use_module|tank_gas_turbine_engine
```


### character_name

![MD]
The character_name formatter gets the name of the character.

### Example:
```
custom_effect_tooltip = character_name|hjalmar_schacht
```


## script_collection_input

### game all_countries

![MD]
All existing countries (including government in exile).
### Example
```
has_resources_in_collection = {
	collection = game:all_countries
	resource = steel
	amount > 799
	extracted = yes
}
```


### game all_possible_countries

![MD]
All countries (including those that doesn't exist).

### Example
```
has_resources_in_collection = {
	collection = collection:all_possible_countries
	resource = steel
	amount > 799
	extracted = yes
}
```


### game all_states

![MD]
All existing states.

### Example
Check if there are more than 42 states in the game.
```
collection_size = {
	input = game:all_states
	value > 42
}
```


### game scope

![MD]
Current scope object.

### Example
Check if there are more than 42 members in the faction of the current scope (assumes current scope is country scope).
```
collection_size = {
    input = {
        input = game:scope
        operators = { faction_members }
    }
	value > 42
}
```


### collection NAME

![MD]
Use a named collection as input.

### Example
Checks if there are more than 42 members in the collection named "my_named_collection".
```
collection_size = {
    input = collection:my_named_collection
    value > 42
}
```


### constant NAME

![MD]
Use a constant as input.
### Example
Checks if there are more than 42 members in the collection named "my_named_collection".
```
collection_size = {
	input = constant:my_constant
	value > 42
}
```

## script_collection_operator

### faction_members

![MD]
Gets all the faction members of the provided country (including the country itself).
The collection will be empty if there are no faction members.

Will be used to localize if used as first operator after an input that accepts operator localization.

### Example
```
collection_size = {
    input = game:all_countries
    operators = { faction_members }
    value > 3
}
```


### owned_states

![MD]
All states owned states by the current country.

Will be used to localize if used as first operator after an input that accepts operator localization.

### Example
```
collection_size = {
    input = game:all_countries
    operators = { owned_states }
    value > 5
}
```


### controlled_states

![MD]
All states controlled by the current country.

Will be used to localize if used as first operator after an input that accepts operator localization.

### Example
```
collection_size = {
    input = game:all_countries
    operators = { controlled_states }
    value > 5
}
```


### country_and_all_subjects

![MD]
The current country and all its subjects.
If the country has no subjects, then the collection will only contain the country itself.

Will be used to localize if used as first operator after an input that accepts operator localization.

### Example
```
collection_size = {
    input = game:scope
    operators = { country_and_all_subjects }
    value > 1
}
```


### limit = PAYLOAD

![MD]
Filters the collection by a trigger.

### Example
```
collection_size = {
    input = game:all_countries
    operators = { trigger = { has_government = democratic } }
    value > 2
}
```


### is_core_of = PAYLOAD

![MD]
Keeps only the states that are a core of the provided country.
The payload to the operator is a scoped variable; scope keywords (`ROOT`, `FROM`, `PREV`) must resolve to a country.
Only valid on state collections.

### Example
```
collection_size = {
    input = game:all_states
    operators = { is_core_of = ROOT }
    value > 5
}
```


### is_not_core_of = PAYLOAD

![MD]
Keeps only the states that are **not** a core of the provided country.
The payload to the operator is a scoped variable; scope keywords (`ROOT`, `FROM`, `PREV`) must resolve to a country.
Only valid on state collections.

### Example
```
collection_size = {
    input = game:all_states
    operators = { is_not_core_of = ROOT }
    value > 5
}
```


## script_math_functions

### multiply

![MD]
Multiplies the accumulator by a value.

### Example
```
{ value = 2.3  multiply = num_units }
```


### add

![MD]
Adds a value to the accumulator.

### Example
```
{ value = 5.0  add = num_factories }
```


### subtract

![MD]
Subtracts a value from the accumulator.

### Example
```
{ value = 20  subtract = 5 }
```


### divide

![MD]
Divides the accumulator by a value.

### Example
```
{ value = 100  divide = 5 }
```


### min

![MD]
Sets the accumulator to the minimum of itself and the value.

### Example
```
{ value = 9  min = 4 }
```


### max

![MD]
Sets the accumulator to the maximum of itself and the value.

### Example
```
{ value = 9  max = 15 }
```


### clamp

![MD]
Clamps the accumulator between a minimum and maximum bound. Note that arguments are order sensitive.

### Example
```
{ value = num_units  clamp = { min = 0 max = 100 } }
```


### lerp

![MD]
Linearly interpolates from the accumulator towards `to` by `alpha`, where alpha is clamped between 0 and 1. An alpha of 0 keeps the accumulator, 1 returns `to`.

### Example
```
{ value = 10  lerp = { to = 20  alpha = 0.5 } }
```


### >

![MD]
Returns 1 if the accumulator is greater than the value, otherwise 0.

### Example
```
{ value = 10  greater_than = 5 }
```


### <

![MD]
Returns 1 if the accumulator is less than the value, otherwise 0.

### Example
```
{ value = 2  less_than = 5 }
```


### greater_than_or_equals

![MD]
Returns 1 if the accumulator is greater than or equal to the value, otherwise 0.

### Example
```
{ value = 5  greater_than_or_equals = 5 }
```


### less_than_or_equals

![MD]
Returns 1 if the accumulator is less than or equal to the value, otherwise 0.

### Example
```
{ value = 5  less_than_or_equals = 5 }
```


### equals

![MD]
Returns 1 if the accumulator equals the value, otherwise 0.

### Example
```
{ value = 7  equals = 7 }
```


### not_equals

![MD]
Returns 1 if the accumulator does not equal the value, otherwise 0.

### Example
```
{ value = 7  not_equals = 5 }
```


### xor

![MD]
Returns 1 if exactly one of the accumulator and the value is non-zero, otherwise 0.

### Example
```
{ value = 1  xor = 0 }
```


### not

![MD]
Returns 1 if the accumulator is zero, otherwise 0.

### Example
```
{ value = 0  not = yes }
```


### round

![MD]
Rounds the accumulator to the nearest integer.

### Example
```
{ value = 3.7  round = yes }
```


### pow

![MD]
Raises the accumulator to the given power.

Integer exponents are computed exactly by repeated multiplication. Fractional exponents (e.g. `pow = 0.5`) use a numerical approximation and may produce small rounding errors; follow with `round = yes` if you need an exact integer result.

### Example
```
{ value = 2  pow = 10 }
{ value = 2  pow = 10  round = yes }
```


### root

![MD]
Takes the root of the accumulator. The argument is the degree of the root, so 2 gives the square root, 3 the cube root and so on.

Note: this is a numerical approximation and may produce small rounding errors (e.g. 4.00001 instead of 4). Follow with `round = yes` if you need an exact integer result.

### Example
```
{ value = 16  root = 2 }
{ value = 27  root = 3 }
{ value = 16  root = 2  round = yes }
```


### mod

![MD]
Sets the accumulator to the remainder of dividing it by the value.

### Example
```
{ value = 17  mod = 5 }
```


### log

![MD]
Sets the accumulator to its logarithm in the given base.

Note: this is computed with a numerical approximation and may produce small rounding errors (e.g. 3.00001 instead of 3). Follow with `round = yes` if you need an exact integer result.

### Example
```
{ value = 1000  log = 10 }
{ value = 1000  log = 10  round = yes }
```


### sin

![MD]
Sets the accumulator to the sine of itself. The angle is expressed in radians.

### Example
```
{ value = 0  sin = yes }
```


### cos

![MD]
Sets the accumulator to the cosine of itself. The angle is expressed in radians.

### Example
```
{ value = 0  cos = yes }
```


### tan

![MD]
Sets the accumulator to the tangent of itself. The angle is expressed in radians.

### Example
```
{ value = 0  tan = yes }
```


### atan

![MD]
Sets the accumulator to the arctangent of itself. The result is expressed in radians.

Note: this is computed with a numerical approximation and may be off by a few hundredths of a radian. Follow with `round = yes` if you need an exact result.

### Example
```
{ value = 1  atan = yes }
```


### atan2

![MD]
Sets the accumulator to the quadrant-aware arctangent atan2(y, x), where the accumulator is y and the value is x. The result is expressed in radians.

Note: this is computed with a numerical approximation and may be off by a few hundredths of a radian; follow with `round = yes` if you need an exact result. The degenerate case atan2(0, 0) returns roughly pi/2 rather than 0.

### Example
```
{ value = 1  atan2 = 1 }
```


### and

![MD]
Returns 1 if both the accumulator and the value are non-zero, otherwise 0.

Short-circuits: the value is only evaluated when the accumulator is non-zero.

### Example
```
{ value = 1  and = 1 }
```


### or

![MD]
Returns 1 if either the accumulator or the value is non-zero, otherwise 0.

Short-circuits: the value is only evaluated when the accumulator is zero.

### Example
```
{ value = 0  or = 1 }
```


### if

![MD]
Conditional statement that modifies the accumulator based on a condition.
Note that the limit is a math expression. It is considered true if the value is anything but 0.

### Example
```
{ value = x
  if = { limit = { value = x  greater_than = 10 }  add = 100 }
  else = { subtract = 1 } }
```


### every_collection

![MD]
Iterates over a named collection, applying statements to the accumulator for each element.

If the body is a single `and` or `or` chain it short-circuits the whole loop: iteration stops as soon
as the accumulator reaches 0 (for `and`) or a non-zero value (for `or`), so it stops scanning once the
result is decided.

### Example
```
{ value = 0
  every_collection = {
    named_collection = my_collection
    add = element_value } }
```


## loc_objects

### Province

{
  "promotions": [
    {
      "doc": "![MD]\nGets the controlling country of the province",
      "name": "Controller"
    },
    {
      "doc": "![MD]\nGets the terrain of the province.",
      "name": "Terrain"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the province.",
      "name": "GetName"
    }
  ]
}

### Operation

{
  "promotions": [
    {
      "doc": "![MD]\nGets the target country of the operation.",
      "name": "Target"
    },
    {
      "doc": "![MD]\nGets the initiator country of the operation.",
      "name": "Initiator"
    },
    {
      "doc": "![MD]\nGets the first operative of the operation.",
      "name": "Operative0"
    },
    {
      "doc": "![MD]\nGets the third operative of the operation.",
      "name": "Operative2"
    },
    {
      "doc": "![MD]\nGets the second operative of the operation.",
      "name": "Operative1"
    },
    {
      "doc": "![MD]\nGets the fourth operative of the operation.",
      "name": "Operative3"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the operation.",
      "name": "GetName"
    }
  ]
}

### Ace

{
  "promotions": [
    {
      "doc": "![MD]\nGets the owner country of the ace.",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the callsign of the ace.",
      "name": "GetCallsign"
    },
    {
      "doc": "![MD]\n\t\t\t\t\t\t\t\t   Gets She if the ace is a female, otherwise He.",
      "name": "GetSheHeCap"
    },
    {
      "doc": "![MD]\nGets Her if the ace is a female, otherwise Him.",
      "name": "GetHerHimCap"
    },
    {
      "doc": "![MD]\nGets Herself if the ace is a female, otherwise Himself.",
      "name": "GetHerselfHimselfCap"
    },
    {
      "doc": "![MD]\nGets her if the ace is a female, otherwise his.",
      "name": "GetHerHis"
    },
    {
      "doc": "![MD]\nGets the name of the wing the ace is in.",
      "name": "GetWing"
    },
    {
      "doc": "![MD]\nGets the short name of the wing the ace is in.",
      "name": "GetWingShort"
    },
    {
      "doc": "![MD]\nGets hers if the ace is a female, otherwise his.",
      "name": "GetHersHis"
    },
    {
      "doc": "![MD]\nGets the surname of the ace.",
      "name": "GetSurname"
    },
    {
      "doc": "![MD]\nGets the type of the ace.",
      "name": "GetAceType"
    },
    {
      "doc": "![MD]\nGets Hers if the ace is a female, otherwise His.",
      "name": "GetHersHisCap"
    },
    {
      "doc": "![MD]\nGets the name of the ace.",
      "name": "GetName"
    },
    {
      "doc": "![MD]\nGets she if the ace is a female, otherwise he.",
      "name": "GetSheHe"
    },
    {
      "doc": "![MD]\nGets her if the ace is a female, otherwise him.",
      "name": "GetHerHim"
    },
    {
      "doc": "![MD]\nGets herself if the ace is a female, otherwise himself.",
      "name": "GetHerselfHimself"
    },
    {
      "doc": "![MD]\nGets the full name of the ace.",
      "name": "GetFullName"
    },
    {
      "doc": "![MD]\nGets Her if the ace is a female, otherwise His.",
      "name": "GetHerHisCap"
    },
    {
      "doc": "![MD]\nGets the name of the region of the mission the ace is on.",
      "name": "GetMissionRegion"
    }
  ]
}

### Scope

{
  "promotions": [
    {
      "doc": "![MD] Gets the player country.",
      "name": "Player"
    },
    {
      "doc": "![MD]\nDoes nothing.",
      "name": "This"
    },
    {
      "doc": "![MD] Does nothing.",
      "name": "THIS"
    },
    {
      "doc": "![MD] Gets the root scope.",
      "name": "Root"
    },
    {
      "doc": "![MD]\nGets the operation of the current scope.",
      "name": "Operation"
    },
    {
      "doc": "![MD]\nGets the unit of the current scope.",
      "name": "Unit"
    },
    {
      "doc": "![MD]\nGets the ace of the current scope.",
      "name": "Ace"
    },
    {
      "doc": "![MD]\nGets the industrial organisation of the current scope.",
      "name": "IndustrialOrganisation"
    },
    {
      "doc": "![MD] Gets the previous scope.",
      "name": "Prev"
    },
    {
      "doc": "![MD]\nGets the character of the current scope.",
      "name": "Character"
    },
    {
      "doc": "![MD]\nGets the purchase contract of the current scope.",
      "name": "PurchaseContract"
    },
    {
      "doc": "![MD]\nGets the country of the current scope.",
      "name": "Country"
    },
    {
      "doc": "![MD] Gets the from scope.",
      "name": "From"
    },
    {
      "doc": "![MD]\nGets the special project of the current scope.",
      "name": "SpecialProject"
    },
    {
      "doc": "![MD]\nGets the state of the current scope.",
      "name": "State"
    },
    {
      "doc": "![MD]\nGets the combatant of the current scope.",
      "name": "Combatant"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the current game year.",
      "name": "GetYear"
    },
    {
      "doc": "![MD]\nGets the current game date.",
      "name": "GetDate"
    },
    {
      "doc": "![MD]\nGets the current game month.",
      "name": "GetMonth"
    },
    {
      "doc": "![MD]\nGets the current game date as a long string.",
      "name": "GetDateText"
    }
  ]
}

### Terrain

{
  "promotions": [],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the terrain.",
      "name": "GetName"
    }
  ]
}

### Character

{
  "promotions": [
    {
      "doc": "![MD]\nGets the owner country of the character.",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the pronoun for the character with an initial capital letter.",
      "name": "GetSheHeCap"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character with an initial capital letter.",
      "name": "GetHerHimCap"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character with an initial capital letter.",
      "name": "GetHerselfHimselfCap"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character.",
      "name": "GetHerHis"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character.",
      "name": "GetHersHis"
    },
    {
      "doc": "![MD]\nGets the ideology of the character.",
      "name": "GetIdeology"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character with an initial capital letter.",
      "name": "GetHersHisCap"
    },
    {
      "doc": "![MD]\nGets the name of the character.",
      "name": "GetName"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character.",
      "name": "GetSheHe"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character.",
      "name": "GetHerHim"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character.",
      "name": "GetHerselfHimself"
    },
    {
      "doc": "![MD]\nGets the ideology group of the character.",
      "name": "GetIdeologyGroup"
    },
    {
      "doc": "![MD]\nGets the pronoun for the character with an initial capital letter.",
      "name": "GetHerHisCap"
    }
  ]
}

### PurchaseContract

{
  "promotions": [
    {
      "doc": "![MD]\nGets the buyer country of the purchase contract.",
      "name": "Buyer"
    },
    {
      "doc": "![MD]\nGets the seller country of the purchase contract.",
      "name": "Seller"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the delivered payment of the purchase contract.",
      "name": "GetDeliveredPayment"
    }
  ]
}

### Country

{
  "promotions": [
    {
      "doc": "![MD]\nGets the original capital state of the current country.",
      "name": "OriginalCapital"
    },
    {
      "doc": "![MD]\nGets the capital state of the current country.",
      "name": "Capital"
    },
    {
      "doc": "![MD]\nGets the overlord country of the current country.",
      "name": "Overlord"
    },
    {
      "doc": "![MD]\nGets the faction leader country of the current country.",
      "name": "FactionLeader"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the current country's leader.",
      "name": "GetLeader"
    },
    {
      "doc": "![MD]\nGets Her if the current country's leader is female, otherwise Him.",
      "name": "GetHerHimCap"
    },
    {
      "doc": "![MD]\nGets the change rate description of the current country's power balance.",
      "name": "GetChangeRateDesc"
    },
    {
      "doc": "![MD]\nGets her if the current country's leader is female, otherwise his.",
      "name": "GetHerHis"
    },
    {
      "doc": "![MD]\nGets the modifier description of the active range of the current country's power balance.",
      "name": "GetActiveRangeModDesc"
    },
    {
      "doc": "![MD]\nGets the definite name of the current country without considering ideology.",
      "name": "GetNonIdeologyNameDef"
    },
    {
      "doc": "![MD]\nGets the modifier description of the current country's power balance.",
      "name": "GetPowerBalanceModDesc"
    },
    {
      "doc": "![MD]\nGets the neutral party of the current country.",
      "name": "GetNeutralParty"
    },
    {
      "doc": "![MD]\nGets Hers if the current country's leader is female, otherwise His.",
      "name": "GetHersHisCap"
    },
    {
      "doc": "![MD]\nGets the name of the current country.",
      "name": "GetName"
    },
    {
      "doc": "![MD]\nGets the name of the current country with its flag.",
      "name": "GetNameWithFlag"
    },
    {
      "doc": "![MD]\nGets the name of the current country's power balance.",
      "name": "GetPowerBalanceName"
    },
    {
      "doc": "![MD]\nGets the ideology of the current country's ruling party as a noun.",
      "name": "GetRulingIdeologyNoun"
    },
    {
      "doc": "![MD]\nGets the definite old name of the current country.",
      "name": "GetOldNameDef"
    },
    {
      "doc": "![MD]\nGets the communist party of the current country.",
      "name": "GetCommunistParty"
    },
    {
      "doc": "![MD]\nGets the democratic party of the current country.",
      "name": "GetDemocraticParty"
    },
    {
      "doc": "![MD]\nGets the tag of the current country.",
      "name": "GetTag"
    },
    {
      "doc": "![MD]\nGets the adjective of the current country without considering ideology.",
      "name": "GetNonIdeologyAdjective"
    },
    {
      "doc": "![MD]\nGets Her if the current country's leader is female, otherwise His.",
      "name": "GetHerHisCap"
    },
    {
      "doc": "![MD]\nGets the rule description of the active range of the current country's power balance.",
      "name": "GetActiveRangeRuleDesc"
    },
    {
      "doc": "![MD]\nGets the activation effect description of the active range of the current country's power balance.",
      "name": "GetActiveRangeActivationEffect"
    },
    {
      "doc": "![MD]\nGets Herself if the current country's leader is female, otherwise Himself.",
      "name": "GetHerselfHimselfCap"
    },
    {
      "doc": "![MD]\nGets She if the current country's leader is female, otherwise He.",
      "name": "GetSheHeCap"
    },
    {
      "doc": "![MD]\nGets the name of the current country's ruling party.",
      "name": "GetRulingParty"
    },
    {
      "doc": "![MD]\nGets the name of the leader of the democratic party of the current country.",
      "name": "GetDemocraticLeader"
    },
    {
      "doc": "![MD]\nGets the capitalized old adjective of the current country.",
      "name": "GetOldAdjectiveCap"
    },
    {
      "doc": "![MD]\nGets the name of the leader of the communistic party of the current country.",
      "name": "GetCommunistLeader"
    },
    {
      "doc": "![MD]\nGets the deactivation effect description of the active range of the current country's power balance.",
      "name": "GetActiveRangeDeactivationEffect"
    },
    {
      "doc": "![MD]\nGets the name of the trending side of the current country's power balance.",
      "name": "GetTrendingSideName"
    },
    {
      "doc": "![MD]\nGets the old adjective of the current country.",
      "name": "GetOldAdjective"
    },
    {
      "doc": "![MD]\nGets the ideology of the current country's ruling party.",
      "name": "GetRulingIdeology"
    },
    {
      "doc": "![MD]\nGets the support of the current country's ruling party.",
      "name": "GetPartySupport"
    },
    {
      "doc": "![MD]\nGets the name of the current country without considering ideology.",
      "name": "GetNonIdeologyName"
    },
    {
      "doc": "![MD]\nGets the manpower of the current country.",
      "name": "GetManpower"
    },
    {
      "doc": "![MD]\nGets the definite name of the current country.",
      "name": "GetNameDef"
    },
    {
      "doc": "![MD]\nGets hers if the current country's leader is female, otherwise his.",
      "name": "GetHersHis"
    },
    {
      "doc": "![MD]\nGets the capitalized definite name of the current country.",
      "name": "GetNameDefCap"
    },
    {
      "doc": "![MD]\nGets she if the current country's leader is female, otherwise he.",
      "name": "GetSheHe"
    },
    {
      "doc": "![MD]\nGets herself if the current country's leader is female, otherwise himself.",
      "name": "GetHerselfHimself"
    },
    {
      "doc": "![MD]\nGets the name of the active range of the current country's power balance.",
      "name": "GetActiveRangeName"
    },
    {
      "doc": "![MD]\nGets the capitalized definite old name of the current country.",
      "name": "GetOldNameDefCap"
    },
    {
      "doc": "![MD]\nGets the name of the leader of the neutral party of the current country.",
      "name": "GetNeutralLeader"
    },
    {
      "doc": "![MD]\nGets the adjective of the current country.",
      "name": "GetAdjective"
    },
    {
      "doc": "![MD]\nGets the name of the current country's intelligence agency.",
      "name": "GetAgency"
    },
    {
      "doc": "![MD]\nGets the icon of the current country's balance of power trend.",
      "name": "GetBopTrendTextIcon"
    },
    {
      "doc": "![MD]\nGets the capitalized adjective of the current country without considering ideology.",
      "name": "GetNonIdeologyAdjectiveCap"
    },
    {
      "doc": "![MD]\nGets the capitalized adjective of the current country.",
      "name": "GetAdjectiveCap"
    },
    {
      "doc": "![MD]\nGets the name of the active side of the current country's power balance.",
      "name": "GetActiveSideName"
    },
    {
      "doc": "![MD]\nGets the flag of the current country.",
      "name": "GetFlag"
    },
    {
      "doc": "![MD]\nGets the name of the current country's faction.",
      "name": "GetFactionName"
    },
    {
      "doc": "![MD]\nGets the name of the right side of the current country's power balance.",
      "name": "GetRightSideName"
    },
    {
      "doc": "![MD]\nGets the fascist party of the current country.",
      "name": "GetFascistParty"
    },
    {
      "doc": "![MD]\nGets the name of the left side of the current country's power balance.",
      "name": "GetLeftSideName"
    },
    {
      "doc": "![MD]\nGets the long name of the current country's ruling party.",
      "name": "GetRulingPartyLong"
    },
    {
      "doc": "![MD]\nGets her if the current country's leader is female, otherwise him.",
      "name": "GetHerHim"
    },
    {
      "doc": "![MD]\nGets the date of the last election in the current country.",
      "name": "GetLastElection"
    },
    {
      "doc": "![MD]\nGets the capitalized definite name of the current country without considering ideology.",
      "name": "GetNonIdeologyNameDefCap"
    },
    {
      "doc": "![MD]\nGets the name of the leader of the facist party of the current country.",
      "name": "GetFascistLeader"
    },
    {
      "doc": "![MD]\nGets the old name of the current country.",
      "name": "GetOldName"
    }
  ]
}

### LocalizationEnvironment

{
  "promotions": [
    {
      "doc": "![MD]\nGets the faction in the localization environment.",
      "name": "Faction"
    },
    {
      "doc": "![MD]\nGets the building in the localization environment.",
      "name": "Building"
    },
    {
      "doc": "![MD]\nGets the province in the localization environment.",
      "name": "Province"
    },
    {
      "doc": "![MD]\nGets the terrain in the localization environment.",
      "name": "Terrain"
    }
  ],
  "properties": []
}

### UnitLeader

{
  "promotions": [
    {
      "doc": "![MD]\nGets the owner country of the unit leader.",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the skill level of the unit leader.",
      "name": "GetLeaderSkill"
    },
    {
      "doc": "![MD]\nGets She if the unit leader is a female, otherwise He.",
      "name": "GetSheHeCap"
    },
    {
      "doc": "![MD]\nGets Her if the unit leader is a female, otherwise Him.",
      "name": "GetHerHimCap"
    },
    {
      "doc": "![MD]\nGets Herself if the unit leader is a female, otherwise Himself.",
      "name": "GetHerselfHimselfCap"
    },
    {
      "doc": "![MD]\nGets her if the unit leader is a female, otherwise his.",
      "name": "GetHerHis"
    },
    {
      "doc": "![MD]\nGets the name of the unit leader.",
      "name": "GetName"
    },
    {
      "doc": "![MD]\nGets she if the unit leader is a female, otherwise he.",
      "name": "GetSheHe"
    },
    {
      "doc": "![MD]\nGets her if the unit leader is a female, otherwise him.",
      "name": "GetHerHim"
    },
    {
      "doc": "![MD]\nGets herself if the unit leader is a female, otherwise himself.",
      "name": "GetHerselfHimself"
    },
    {
      "doc": "![MD]\nGets the rank of the unit leader.",
      "name": "GetRank"
    },
    {
      "doc": "![MD]\nGets the codename of the operative leader.",
      "name": "GetCodeName"
    },
    {
      "doc": "![MD]\nGets Her if the unit leader is a female, otherwise His.",
      "name": "GetHerHisCap"
    }
  ]
}

### Building

{
  "promotions": [],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the building.",
      "name": "GetName"
    }
  ]
}

### SpecialProject

{
  "promotions": [
    {
      "doc": "![MD]\nGets the owner country of the special project.",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the special project",
      "name": "GetName"
    }
  ]
}

### State

{
  "promotions": [
    {
      "doc": "![MD]\nGets the controller country of the state.",
      "name": "Controller"
    },
    {
      "doc": "![MD]\nGets the occupied country of the state.",
      "name": "Occupied"
    },
    {
      "doc": "![MD]\nGets the owner country of the state.",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the ID of the state.",
      "name": "GetID"
    },
    {
      "doc": "![MD]\nGets the name of the capital victory point of the state.",
      "name": "GetCapitalVictoryPointName"
    },
    {
      "doc": "![MD]\nGets the name of the state.",
      "name": "GetName"
    },
    {
      "doc": "![MD]\nGets the name of the continent this state is in.",
      "name": "GetContinent"
    }
  ]
}

### IndustrialOrg

{
  "promotions": [
    {
      "doc": "![MD]\nGets the owner country of the industrial organisation",
      "name": "Owner"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the industrial organisation",
      "name": "GetName"
    }
  ]
}

### Faction

{
  "promotions": [
    {
      "doc": "![MD] Gets the leader of the faction",
      "name": "Leader"
    }
  ],
  "properties": [
    {
      "doc": "![MD]\nGets the name of the faction.",
      "name": "GetName"
    }
  ]
}

## dynamic_variables

### global

{
  "year": {
    "description": "current year"
  },
  "province_controllers": {
    "description": "get array of all province controllers. Example: province_controllers^4135"
  },
  "states": {
    "description": "get array of all states"
  },
  "num_days": {
    "description": "current total days"
  },
  "date": {
    "description": "get date value that can be comparable to other date values and localized using GetDateString/GetDateStringShortMonth/GetDateStringNoHour/GetDateStringNoHourLong scripted locs"
  },
  "global_resource_extracted_total": {
    "description": "total amount of resources extracted by the world"
  },
  "countries": {
    "description": "get array of all countries (including non existing"
  },
  "majors": {
    "description": "get array of all majors (including non existing"
  },
  "global_resource_extracted": {
    "description": "total amount of specific resource extracted by the world, resource type is defined in target global_resource_extracted@steel"
  },
  "ideology_groups": {
    "description": "array of objects in ideology_groups database"
  },
  "operations": {
    "description": "array of objects in operations database"
  },
  "technology": {
    "description": "array of objects in technology database"
  },
  "difficulty": {
    "description": "check if the difficulty is above or below specified value 0-2 (difficulty enum). Example: difficulty > 0 (above easy)",
    "is_trigger": true
  },
  "threat": {
    "description": "check the global threat value (world tension). 0-1 value",
    "is_trigger": true
  },
  "pc_turn": {
    "description": "Checks turn number in PC.\nExample:\npc_turn > 20",
    "is_trigger": true
  },
  "power_balance_value": {
    "description": "compares current value of a power balance\n\nExample:\npower_balance_value = {\n\tid = power_balance_id\n\tvalue > 0.5 # supported operators are: >, < and =\n}",
    "is_trigger": true
  },
  "power_balance_daily_change": {
    "description": "compares current total daily change of a power balance\n\nExample:\npower_balance_daily_change = {\n\tid = power_balance_id\n\tvalue > 0.5 # supported operators are: >, < and =\n}",
    "is_trigger": true
  },
  "power_balance_weekly_change": {
    "description": "compares current total weekly change of a power balance\n\nExample:\npower_balance_weekly_change = {\n\tid = power_balance_id\n\tvalue > 0.5 # supported operators are: >, < and =\n}",
    "is_trigger": true
  },
  "num_of_career_profile_points": {
    "description": "check amount of gained career points",
    "is_trigger": true
  }
}

### country

{
  "manpower_k": {
    "description": "total manpower of country in thousands"
  },
  "political_power": {
    "description": "total political power of country"
  },
  "num_owned_states": {
    "description": "number of owned states"
  },
  "manpower": {
    "description": "DEPRECATED, MAY OVERFLOW. total manpower of country"
  },
  "stability": {
    "description": "stability of a country"
  },
  "air_intel": {
    "description": "air intel against a target country. example GER.air_intel@ENG"
  },
  "command_power": {
    "description": "total command power of country"
  },
  "total_equipment_produced_screen_ship": {
    "description": "Total produced equipment of typescreen_ship"
  },
  "deployed_airforce_manpower_k": {
    "description": "total deployed air manpower of country in thousands. Does not include exile manpower"
  },
  "num_of_owned_factories": {
    "description": "check the number of factories in owned states excluding any gained or lost through trade, relations, modifiers etc.",
    "is_trigger": true
  },
  "num_orders_groups": {
    "description": "number of orders groups"
  },
  "num_core_states": {
    "description": "number of core states"
  },
  "deployed_navy_manpower_k": {
    "description": "total deployed navy manpower of country in thousands."
  },
  "deployed_army_manpower_k": {
    "description": "total deployed army manpower of country in thousands."
  },
  "num_equipment": {
    "description": "number of equipment in country. example num_equipment@infantry_equipment"
  },
  "deployed_total_manpower_k": {
    "description": "total deployed manpower of country in thousands."
  },
  "faction_influence_ratio": {
    "description": "![MD]\n Checks influence ratio of current country in the faction\n\n### Examples\n```\n TAG = {\n\tfaction_influence_ratio > 0.1\n}\n```\n",
    "is_trigger": true
  },
  "days_until_next_election": {
    "description": "days until the next election. -1 if never"
  },
  "high_command": {
    "description": "returns an array with the currently hired high command of the country"
  },
  "max_available_manpower": {
    "description": "DEPRECATED, MAY OVERFLOW. total available manpower of country"
  },
  "fuel_k": {
    "description": "total fuel of country in thousands"
  },
  "max_fuel_k": {
    "description": "max fuel of country in thousands"
  },
  "ai_attitude_outraged_weight": {
    "description": "weight for an ai attitude attitude_outragedagainst country. Example: GER.ai_attitude_outraged_weight@ENG"
  },
  "max_available_manpower_k": {
    "description": "total available manpower of country in thousands"
  },
  "autonomy_ratio": {
    "description": "autonomy of scope country. -1 if not a subject"
  },
  "max_manpower": {
    "description": "DEPRECATED, MAY OVERFLOW. maximum manpower of country"
  },
  "max_manpower_k": {
    "description": "maximum manpower of country in thousands"
  },
  "ai_strategy_support": {
    "description": "ai strategy value support against country. Example: GER.ai_strategy_support@ENG"
  },
  "opinion": {
    "description": "opinion of a country targeted on another one. example GER.opinion@ENG"
  },
  "army_experience": {
    "description": "army experience of a country"
  },
  "controlled_states": {
    "description": "array of controlled states"
  },
  "navy_experience": {
    "description": "navy experience of a country"
  },
  "highest_party_popularity": {
    "description": "popularity size of the most popular party [0.00, 1.00]. Can exclude the ruling party by using @exclude_ruling_party. Example: highest_party_popularity OR highest_party_popularity@exclude_ruling_party"
  },
  "navy_intel": {
    "description": "navy intel against a target country. example GER.navy_intel@ENG"
  },
  "total_equipment_produced_rocket": {
    "description": "Total produced equipment of typerocket"
  },
  "resource_consumed": {
    "description": "number of resources consumed by country, resource type is defined in target resource_consumed@steel"
  },
  "air_experience": {
    "description": "air experience of a country"
  },
  "ai_attitude_friendly_weight": {
    "description": "weight for an ai attitude attitude_friendlyagainst country. Example: GER.ai_attitude_friendly_weight@ENG"
  },
  "num_battalions_with_type": {
    "description": "number of battalions with sub unit type, sub unit type is defined in target. example: num_battalions_with_type@light_armor"
  },
  "foreign_manpower": {
    "description": "check the amount of foreign garrison manpower we have",
    "is_trigger": true
  },
  "num_armies": {
    "description": "number of armies"
  },
  "total_constructed_naval_fort": {
    "description": "Total constructions of naval_fort"
  },
  "civilian_intel": {
    "description": "civilian intel against a target country. example GER.civilian_intel@ENG"
  },
  "num_ships": {
    "description": "number of ships"
  },
  "num_deployed_planes": {
    "description": "number of deployed planes"
  },
  "potential_and_current_enemies": {
    "description": "array of potential and actual enemies"
  },
  "num_deployed_planes_with_type": {
    "description": "number of deployed planes with equipment type. example num_deployed_planes_with_type@fighter"
  },
  "total_equipment_produced_emplacement_gun_ammo": {
    "description": "Total produced equipment of typeemplacement_gun_ammo"
  },
  "casualties": {
    "description": "Check the amount of casualties a country has suffered in all of it's wars",
    "is_trigger": true
  },
  "capital": {
    "description": "capital state of the country"
  },
  "army_intel": {
    "description": "army intel against a target country. example GER.army_intel@ENG"
  },
  "navy_chief": {
    "description": "returns the currently hired navy chief of the country"
  },
  "num_armies_in_state": {
    "description": "number of armies in state, state is in target. example num_armies_in_state@123"
  },
  "total_equipment_produced_nuclear_missile": {
    "description": "Total produced equipment of typenuclear_missile"
  },
  "num_of_controlled_factories": {
    "description": "check the number of factories in controlled states excluding any gained or lost through trade, relations, modifiers etc.",
    "is_trigger": true
  },
  "num_controlled_states": {
    "description": "number of controlled states"
  },
  "num_ships_with_type": {
    "description": "number of ships controlled in country, ship type is defined in target. example num_ships_with_type@carrier. can be a sub unit def type or one of carrier,capital,screen, submarine"
  },
  "num_armies_with_type": {
    "description": "number of armies with dominant type, dominant type is defined in target. example: num_armies_with_type@light_armor"
  },
  "num_battalions": {
    "description": "number of battalions"
  },
  "modifier": {
    "description": "a modifier stored in country scope"
  },
  "enemies": {
    "description": "array of enemies at war with"
  },
  "party_popularity": {
    "description": "popularity of targeted party [0.00, 1.00]. example party_popularity@democratic. May also target ruling_party. This also supports country variables, so you can party_popularity@my_var_name for variables that store ideologies"
  },
  "host": {
    "description": "exile host of this country"
  },
  "party_popularity_100": {
    "description": "popularity of targeted party [0.00, 100.00]. example party_popularity_100@democratic. May also target ruling_party. This also supports country variables, so you can party_popularity_100@my_var_name for variables that store ideologies"
  },
  "researched_techs": {
    "description": "returns the array of researched technologies"
  },
  "days_mission_timeout": {
    "description": "timeout in days for a specific timed mission, mission type token is defined in target. example: days_mission_timeout@GER_mefo_bills_mission"
  },
  "total_equipment_produced_anti_tank": {
    "description": "Total produced equipment of typeanti_tank"
  },
  "faction_leader": {
    "description": "faction leader of this country's faction"
  },
  "highest_party_ideology": {
    "description": "ideology of the most popular party. Can exclude the ruling party by using @exclude_ruling_party. Example: highest_party_ideology OR highest_party_ideology@exclude_ruling_party"
  },
  "core_resistance": {
    "description": "returns core resistance of target country"
  },
  "current_party_ideology_group": {
    "description": "returns the token for current party ideology group"
  },
  "owned_states": {
    "description": "array of owned states"
  },
  "core_states": {
    "description": "array of core states"
  },
  "num_owned_controlled_states": {
    "description": "number of owned and core states"
  },
  "ai_strategy_prepare_for_war": {
    "description": "ai strategy value prepare_for_war against country. Example: GER.ai_strategy_prepare_for_war@ENG"
  },
  "overlord": {
    "description": "master of this subject"
  },
  "owned_controlled_states": {
    "description": "array owned and core states"
  },
  "enemies_of_allies": {
    "description": "array of enemies of allies"
  },
  "subjects": {
    "description": "array of subjects"
  },
  "neighbors": {
    "description": "array of neighbors"
  },
  "has_war_support": {
    "description": "check value of war_support 0-1: Example has_war_support < 0.6",
    "is_trigger": true
  },
  "neighbors_owned": {
    "description": "array of neighbors to owned states"
  },
  "any_war_score": {
    "description": "compares the warscore of all wars in a country to see if any fullfills the comparison condition 0-100 - Example: any_war_score > 40",
    "is_trigger": true
  },
  "exiles": {
    "description": "exile host of this country"
  },
  "country_leader": {
    "description": "returns the current country leader of the country"
  },
  "allies": {
    "description": "array of allies (faction members). prefer using faction_members instead"
  },
  "faction_members": {
    "description": "array of faction members"
  },
  "days_decision_timeout": {
    "description": "timeout in days for a specific timed decision, decision type token is defined in target. example: days_decision_timeout@SOV_propaganda_knowledge"
  },
  "resource_produced": {
    "description": "number of resources produced by country, resource type is defined in target. example resource_produced@steel"
  },
  "resource_exported": {
    "description": "number of resources exported by country, resource type is defined in target resource_exported@steel"
  },
  "resource_imported": {
    "description": "number of resources imported by country, resource type is defined in target resource_imported@steel"
  },
  "faction_resource_extracted_total": {
    "description": "total amount of resources extracted by the country's faction"
  },
  "num_nukes_being_dropped": {
    "description": "total number of nukes that are currently ready to be dropped",
    "is_trigger": true
  },
  "faction_resource_extracted": {
    "description": "total amount of specific resource extracted by the country's faction, resource type is defined in target faction_resource_extracted@steel"
  },
  "total_equipment_produced_heavy_fighter": {
    "description": "Total produced equipment of typeheavy_fighter"
  },
  "resource": {
    "description": "number of surplus resources in country, resource type is defined in target resource@steel"
  },
  "legitimacy": {
    "description": "legitimacy of scope country. -1 if not an exile"
  },
  "num_equipment_in_armies": {
    "description": "number of equipment in armies of the country, equipment type token is defined in target. example num_equipment_in_armies@infantry_equipment"
  },
  "num_target_equipment_in_armies": {
    "description": "number of equipment required in armies of the country, equipment type token is defined in target. example num_target_equipment_in_armies@infantry_equipment"
  },
  "total_equipment_produced_maritime_patrol_plane": {
    "description": "Total produced equipment of typemaritime_patrol_plane"
  },
  "total_constructed_anti_air": {
    "description": "Total constructions of anti_air"
  },
  "num_faction_members": {
    "description": "Compares the number of members in the faction for the current country. \n Example: num_faction_members > 10",
    "is_trigger": true
  },
  "num_equipment_in_armies_k": {
    "description": "number of equipment in armies of the country in thousands, equipment type token is defined in target. example num_equipment_in_armies_k@infantry_equipment"
  },
  "num_target_equipment_in_armies_k": {
    "description": "number of equipment required in armies of the country in thousands, equipment type token is defined in target. example num_target_equipment_in_armies_k@infantry_equipment"
  },
  "ai_attitude_wants_antagonize": {
    "description": "returns 1 if ai wants antagonize"
  },
  "ai_attitude_wants_weaken": {
    "description": "returns 1 if ai wants weaken"
  },
  "ai_attitude_wants_ally": {
    "description": "returns 1 if ai wants ally"
  },
  "num_free_operative_slots": {
    "description": "Checks the number of operative a country can recruit right now.\nNote that this is not necessarily greater than zero if num_operative_slots returned a number greater than the number of operative.",
    "is_trigger": true
  },
  "ai_attitude_wants_protect": {
    "description": "returns 1 if ai wants protect"
  },
  "casualties_k": {
    "description": "Check the amount of casualties in thousands a country has suffered in all of it's wars",
    "is_trigger": true
  },
  "ai_attitude_wants_ignore": {
    "description": "returns 1 if ai wants ignore"
  },
  "ai_strategy_contain": {
    "description": "ai strategy value contain against country. Example: GER.ai_strategy_contain@ENG"
  },
  "ai_attitude_is_threatened": {
    "description": "returns 1 if ai is threatened"
  },
  "core_compliance": {
    "description": "returns core compliance of target country"
  },
  "has_added_tension_amount": {
    "description": "Compare if the country has added above or below the specified ammount of tension",
    "is_trigger": true
  },
  "occupied_countries": {
    "description": "array of occupied countries"
  },
  "original_tag": {
    "description": "returns the original tag of a country"
  },
  "total_constructed_dockyard": {
    "description": "Total constructions of dockyard"
  },
  "encryption_strength": {
    "description": "total encryption strength of a country that is needed"
  },
  "decryption_speed": {
    "description": "total encryption strength of a country that is needed"
  },
  "ai_irrationality": {
    "description": "check the ai irrationality value",
    "is_trigger": true
  },
  "num_of_controlled_states": {
    "description": "check amount of controlled stats",
    "is_trigger": true
  },
  "cryptology_defense_level": {
    "description": "cryptology defense level of a country"
  },
  "army_leaders": {
    "description": "all army leaders of a country"
  },
  "navy_leaders": {
    "description": "all navy leaders of a country"
  },
  "num_researched_technologies": {
    "description": "Number of researched technologies",
    "is_trigger": true
  },
  "operatives": {
    "description": "all operatives of a country"
  },
  "power_balance_value": {
    "description": "current power balance value"
  },
  "power_balance_daily": {
    "description": "current total power balance daily change"
  },
  "power_balance_weekly": {
    "description": "current total power balance weekly change"
  },
  "total_constructed_civilian_factory": {
    "description": "Total constructions of civilian_factory"
  },
  "theorist": {
    "description": "returns the currently hired theorist of the country"
  },
  "army_chief": {
    "description": "returns the currently hired army chief of the country"
  },
  "air_chief": {
    "description": "returns the currently hired air chief of the country"
  },
  "political_advisor": {
    "description": "returns an array with the currently hired political advisors of the country"
  },
  "num_of_civilian_factories_in_cores": {
    "description": "calculates the number of civilian factories on core states of current country scope, on those states that are under control of @Tag <Tag | ROOT | my_var> example num_of_civilian_factories_in_cores@GER"
  },
  "total_equipment_produced_fighter": {
    "description": "Total produced equipment of typefighter"
  },
  "total_constructed_military_factory": {
    "description": "Total constructions of military_factory"
  },
  "amount_research_slots": {
    "description": "check number of research current research slots \n amount_research_slots > 2",
    "is_trigger": true
  },
  "num_of_military_factories_in_cores": {
    "description": "calculates the number of civilian factories on core states of current country scope, on those states that are under control of @Tag  <Tag | ROOT | my_var> example num_of_military_factories_in_cores@GER"
  },
  "num_of_naval_factories_in_cores": {
    "description": "calculates the number of civilian factories on core states of current country scope, on those states that are under control of @Tag  <Tag | ROOT | my_var> example num_of_naval_factories_in_cores@my_var"
  },
  "convoys_destroyed": {
    "description": "total number of convoys destroyed by this country"
  },
  "total_equipment_produced_capital_ship": {
    "description": "Total produced equipment of typecapital_ship"
  },
  "network_national_coverage": {
    "description": "checks network national coverage you have over a country. Example: \nnetwork_national_coverage = { \n target = GER\n value > 0.5\n} \n",
    "is_trigger": true
  },
  "num_of_supply_nodes": {
    "description": "check amount of supply nodes",
    "is_trigger": true
  },
  "ai_strategy_protect": {
    "description": "ai strategy value protect against country. Example: GER.ai_strategy_protect@ENG"
  },
  "energy_ratio": {
    "description": "energy_ratio > 0.8 - Compare current energy fulfilment to the factories, with 1 being 100% and 0 being 0%",
    "is_trigger": true
  },
  "faction_power_projection": {
    "description": "![MD]\nChecks power value of current country's faction projection\n\n### Examples\n```\nTAG = {\n\tfaction_power_projection > VALUE\n}\n```\n",
    "is_trigger": true
  },
  "faction_influence_score": {
    "description": "![MD]\n Checks influence value of current country in the faction\n\n### Examples\n```\n TAG = {\n\tfaction_influence_score > 100\n}\n```\n",
    "is_trigger": true
  },
  "num_of_military_factories": {
    "description": "check amount of military factories",
    "is_trigger": true
  },
  "num_of_civilian_factories": {
    "description": "check amount of civilian factories",
    "is_trigger": true
  },
  "mine_threat": {
    "description": "A trigger to check how dangerous enemy mines are for a country. Controlled by NAVAL_MINE_DANGER defines. Returns a value between 0 and 1. Example mine_threat > 0.5 ",
    "is_trigger": true
  },
  "num_of_naval_factories": {
    "description": "check amount of naval factories",
    "is_trigger": true
  },
  "num_tech_sharing_groups": {
    "description": "checks how many groups a nation is a member of",
    "is_trigger": true
  },
  "num_of_nukes": {
    "description": "check amount of nukes",
    "is_trigger": true
  },
  "surrender_progress": {
    "description": "check if a country is close to surrendering",
    "is_trigger": true
  },
  "has_manpower": {
    "description": "check amount of manpower",
    "is_trigger": true
  },
  "has_political_power": {
    "description": "check amount of political power",
    "is_trigger": true
  },
  "num_of_available_military_factories": {
    "description": "check amount of available military factories",
    "is_trigger": true
  },
  "num_of_available_naval_factories": {
    "description": "check amount of available naval factories",
    "is_trigger": true
  },
  "num_of_available_civilian_factories": {
    "description": "check amount of available civilian factories",
    "is_trigger": true
  },
  "ai_strategy_occupation_policy": {
    "description": "ai strategy value occupation_policy against country. Example: GER.ai_strategy_occupation_policy@ENG"
  },
  "num_divisions": {
    "description": "Will compare towards the amount of divisions a country has control over, if strength matters use has_army_size.",
    "is_trigger": true
  },
  "political_power_daily": {
    "description": "Checks if daily political power increase is more or less that specified value \n political_power_daily > 1.5",
    "is_trigger": true
  },
  "has_bombing_war_support": {
    "description": "check value of bombing malus to war support 0-1: Example has_bombing_war_support < 0.1",
    "is_trigger": true
  },
  "has_stability": {
    "description": "check value of stability 0-1: Example has_stability < 0.6",
    "is_trigger": true
  },
  "has_casualties_war_support": {
    "description": "check value of casualties malus to war support 0-1: Example has_casualties_war_support < 0.1",
    "is_trigger": true
  },
  "has_convoys_war_support": {
    "description": "check value of convoys sunk malus to war support 0-1: Example has_convoys_war_support < 0.1",
    "is_trigger": true
  },
  "land_doctrine_level": {
    "description": "checks researched land doctrine level",
    "is_trigger": true
  },
  "num_of_factories": {
    "description": "Check amount of available factories (excluding temporary sources like trade and lend-lease)\nExample:\nGER = { num_of_factories < 50 }",
    "is_trigger": true
  },
  "original_research_slots": {
    "description": "check number of research slots at start of game",
    "is_trigger": true
  },
  "ai_wants_divisions": {
    "description": "Will compare towards the amount of divisions an ai wants to have.",
    "is_trigger": true
  },
  "alliance_strength_ratio": {
    "description": "Compares the estimated army strength between the scope country, his allies and his enemies.",
    "is_trigger": true
  },
  "enemies_strength_ratio": {
    "description": "Compares the estimated army strength between the scope country and all its enemies",
    "is_trigger": true
  },
  "compare_autonomy_progress_ratio": {
    "description": "check if autonomy progress ratio is higher than value, example:\ncompare_autonomy_progress_ratio > 0.5",
    "is_trigger": true
  },
  "fuel_ratio": {
    "description": "Compares the fuel ratio to a variable.\nExample: fuel_ratio > 0.5",
    "is_trigger": true
  },
  "num_subjects": {
    "description": "check the number of subjects of nation",
    "is_trigger": true
  },
  "num_occupied_states": {
    "description": "check the number of states occupied by nation",
    "is_trigger": true
  },
  "manpower_per_military_factory": {
    "description": "Number of available manpower per factory the country has. Excluding dockyards.\nmanpower_per_military_factory < 1000",
    "is_trigger": true
  },
  "enemies_naval_strength_ratio": {
    "description": "Compares the estimated navy strength between the scope country and all its enemies",
    "is_trigger": true
  },
  "alliance_naval_strength_ratio": {
    "description": "Compares the estimated naval strength between the scope country, his allies and his enemies.",
    "is_trigger": true
  },
  "command_power_daily": {
    "description": "Checks if daily command power increase is more or less that specified value \n command_power_daily > 1.5",
    "is_trigger": true
  },
  "ai_strategy_send_volunteers_desire": {
    "description": "ai strategy value send_volunteers_desire against country. Example: GER.ai_strategy_send_volunteers_desire@ENG"
  },
  "num_of_civilian_factories_available_for_projects": {
    "description": "check amount of civilian factories available for a new project to use",
    "is_trigger": true
  },
  "political_power_growth": {
    "description": "Check the value of political power daily growth.Exacmple: political_power_growth > 0",
    "is_trigger": true
  },
  "amount_manpower_in_deployment_queue": {
    "description": "Checks for amount manpower currently in deploymentview. amount_manpower_in_training > 10",
    "is_trigger": true
  },
  "pc_total_score": {
    "description": "Checks country's total peace conference score. Only usable if the country is on the winning side.\nExample:\nCZE = { pc_total_score > 400 }",
    "is_trigger": true
  },
  "pc_current_score": {
    "description": "Checks country's total peace conference score. Only usable if the country is on the winning side.\nExample:\nCZE = { pc_current_score > 400 }",
    "is_trigger": true
  },
  "has_legitimacy": {
    "description": "Check scope country legitimacy 0-100: Example has_legitimacy < 60",
    "is_trigger": true
  },
  "days_since_capitulated": {
    "description": "Checks the number of days since the country last capitulated, even if it is no longer capitulated.\n\tIf it has not ever capitulated, the value is extremely large.\n\tIt is recommended to combine this with has_capitulated = yes when you specifically want to ignore non-active capitulations.\nExamples:\n\tHOL = { has_capitulated = yes days_since_capitulated > 60 } # The Netherlands has been capitulated for more than two months\n\tFRA = { has_capitulated = yes days_since_capitulated < 21 } # France has capitulated sometime within the past three weeks\n\tGER = { OR = { has_capitulated = no days_since_capitulated > 14 } } # Germany is not both actively and recently capitulated\n",
    "is_trigger": true
  },
  "convoy_threat": {
    "description": "A trigger to check convoy threat for a country. Controlled by NAVAL_CONVOY_DANGER defines. Returns a value between 0 and 1. Example convoy_threat > 0.5 ",
    "is_trigger": true
  },
  "longest_war_length": {
    "description": "Check number of months the country has been at war",
    "is_trigger": true
  },
  "decryption_progress": {
    "description": "checks decryption ratio against a country. Example: \ndecryption_progress = { \n target = GER\n value > 0.5\n} \n#or decryption_progress@GER as variable\n",
    "is_trigger": true
  },
  "garrison_manpower_need": {
    "description": "check the amount of manpower needed by garrisons",
    "is_trigger": true
  },
  "total_equipment_produced_armor": {
    "description": "Total produced equipment of typearmor"
  },
  "agency_upgrade_number": {
    "description": "Checks the number of upgrade done in the intelligence agency. \nagency_upgrade_number > 4",
    "is_trigger": true
  },
  "num_of_operatives": {
    "description": "Checks the number of operatives the country controls",
    "is_trigger": true
  },
  "num_operative_slots": {
    "description": "Checks the number of available operative slots a country has.\nIf this differs from the number of operative, this does not mean the country can recruit an operative, but that it will eventually be able to.",
    "is_trigger": true
  },
  "num_fake_intel_divisions": {
    "description": "Will compare towards the amount of fake intel divisions a country has control over. .",
    "is_trigger": true
  },
  "has_collaboration": {
    "description": "checks the collaboration in a target country with our currently scoped country. Example: \nhas_collaboration = { \n target = GER\n value > 0.5\n} \n#or has_collaboration@GER as variable\n",
    "is_trigger": true
  },
  "num_nukes_left_to_drop": {
    "description": "number of nukes left to drop during this game tick (only useful in-between nuke drops, like in on_nuke_drop on-action, for example)",
    "is_trigger": true
  },
  "faction_manifest_fulfillment": {
    "description": "![MD]\nChecks manifest fulfillment value of current country's faction manifest\n\n### Examples\n```\nTAG = {\n\tfaction_manifest_fulfillment > VALUE\n}\n```\n",
    "is_trigger": true
  },
  "total_equipment_produced_air_transport": {
    "description": "Total produced equipment of typeair_transport"
  },
  "faction_influence_rank": {
    "description": "![MD]\nChecks influence rank in the faction of the current country\n\n### Examples\n```\nTAG = {\n\tfaction_influence_rank < 5\n}\n```\n",
    "is_trigger": true
  },
  "ai_strategy_conquer": {
    "description": "ai strategy value conquer against country. Example: GER.ai_strategy_conquer@ENG"
  },
  "ai_strategy_antagonize": {
    "description": "ai strategy value antagonize against country. Example: GER.ai_strategy_antagonize@ENG"
  },
  "ai_strategy_invade": {
    "description": "ai strategy value invade against country. Example: GER.ai_strategy_invade@ENG"
  },
  "ai_strategy_befriend": {
    "description": "ai strategy value befriend against country. Example: GER.ai_strategy_befriend@ENG"
  },
  "ai_strategy_consider_weak": {
    "description": "ai strategy value consider_weak against country. Example: GER.ai_strategy_consider_weak@ENG"
  },
  "total_equipment_produced_flame": {
    "description": "Total produced equipment of typeflame"
  },
  "ai_strategy_alliance": {
    "description": "ai strategy value alliance against country. Example: GER.ai_strategy_alliance@ENG"
  },
  "ai_strategy_influence": {
    "description": "ai strategy value influence against country. Example: GER.ai_strategy_influence@ENG"
  },
  "ai_strategy_dont_defend_ally_borders": {
    "description": "ai strategy value dont_defend_ally_borders against country. Example: GER.ai_strategy_dont_defend_ally_borders@ENG"
  },
  "ai_strategy_force_defend_ally_borders": {
    "description": "ai strategy value force_defend_ally_borders against country. Example: GER.ai_strategy_force_defend_ally_borders@ENG"
  },
  "ai_strategy_ignore_claim": {
    "description": "ai strategy value ignore_claim against country. Example: GER.ai_strategy_ignore_claim@ENG"
  },
  "ai_strategy_ignore": {
    "description": "ai strategy value ignore against country. Example: GER.ai_strategy_ignore@ENG"
  },
  "ai_strategy_decrypt_target": {
    "description": "ai strategy value decrypt_target against country. Example: GER.ai_strategy_decrypt_target@ENG"
  },
  "ai_strategy_declare_war": {
    "description": "ai strategy value declare_war against country. Example: GER.ai_strategy_declare_war@ENG"
  },
  "ai_strategy_activate_crypto": {
    "description": "ai strategy value activate_crypto against country. Example: GER.ai_strategy_activate_crypto@ENG"
  },
  "ai_attitude_neutral_weight": {
    "description": "weight for an ai attitude attitude_neutralagainst country. Example: GER.ai_attitude_neutral_weight@ENG"
  },
  "ai_attitude_hostile_weight": {
    "description": "weight for an ai attitude attitude_hostileagainst country. Example: GER.ai_attitude_hostile_weight@ENG"
  },
  "ai_attitude_protective_weight": {
    "description": "weight for an ai attitude attitude_protectiveagainst country. Example: GER.ai_attitude_protective_weight@ENG"
  },
  "ai_attitude_threatened_weight": {
    "description": "weight for an ai attitude attitude_threatenedagainst country. Example: GER.ai_attitude_threatened_weight@ENG"
  },
  "ai_attitude_allied_weight": {
    "description": "weight for an ai attitude attitude_alliedagainst country. Example: GER.ai_attitude_allied_weight@ENG"
  },
  "total_constructed_port": {
    "description": "Total constructions of port"
  },
  "total_constructed_infrastructure": {
    "description": "Total constructions of infrastructure"
  },
  "total_constructed_air_base": {
    "description": "Total constructions of air_base"
  },
  "total_constructed_rocket_site": {
    "description": "Total constructions of rocket_site"
  },
  "total_constructed_gun_emplacement": {
    "description": "Total constructions of gun_emplacement"
  },
  "total_constructed_radar": {
    "description": "Total constructions of radar"
  },
  "total_constructed_refinery": {
    "description": "Total constructions of refinery"
  },
  "total_constructed_fuel_silo": {
    "description": "Total constructions of fuel_silo"
  },
  "total_constructed_supply_node": {
    "description": "Total constructions of supply_node"
  },
  "total_constructed_nuclear_reactor": {
    "description": "Total constructions of nuclear_reactor"
  },
  "total_constructed_land_fort": {
    "description": "Total constructions of land_fort"
  },
  "total_constructed_naval_headquarter": {
    "description": "Total constructions of naval_headquarter"
  },
  "total_constructed_naval_supply_hub": {
    "description": "Total constructions of naval_supply_hub"
  },
  "total_constructed_other": {
    "description": "Total constructions of other"
  },
  "total_equipment_produced_convoy": {
    "description": "Total produced equipment of typeconvoy"
  },
  "total_equipment_produced_train": {
    "description": "Total produced equipment of typetrain"
  },
  "total_equipment_produced_floating_harbor": {
    "description": "Total produced equipment of typefloating_harbor"
  },
  "total_equipment_produced_naval_bomber": {
    "description": "Total produced equipment of typenaval_bomber"
  },
  "total_equipment_produced_railway_gun": {
    "description": "Total produced equipment of typerailway_gun"
  },
  "total_equipment_produced_land_cruiser": {
    "description": "Total produced equipment of typeland_cruiser"
  },
  "total_equipment_produced_motorized": {
    "description": "Total produced equipment of typemotorized"
  },
  "total_equipment_produced_mechanized": {
    "description": "Total produced equipment of typemechanized"
  },
  "total_equipment_produced_infantry": {
    "description": "Total produced equipment of typeinfantry"
  },
  "total_equipment_produced_submarine": {
    "description": "Total produced equipment of typesubmarine"
  },
  "total_equipment_produced_support_ship": {
    "description": "Total produced equipment of typesupport_ship"
  },
  "total_equipment_produced_interceptor": {
    "description": "Total produced equipment of typeinterceptor"
  },
  "total_equipment_produced_tactical_bomber": {
    "description": "Total produced equipment of typetactical_bomber"
  },
  "total_equipment_produced_strategic_bomber": {
    "description": "Total produced equipment of typestrategic_bomber"
  },
  "total_equipment_produced_cas": {
    "description": "Total produced equipment of typecas"
  },
  "total_equipment_produced_missile": {
    "description": "Total produced equipment of typemissile"
  },
  "total_equipment_produced_ballistic_missile": {
    "description": "Total produced equipment of typeballistic_missile"
  },
  "total_equipment_produced_sam_missile": {
    "description": "Total produced equipment of typesam_missile"
  },
  "total_equipment_produced_suicide": {
    "description": "Total produced equipment of typesuicide"
  },
  "total_equipment_produced_scout_plane": {
    "description": "Total produced equipment of typescout_plane"
  },
  "total_equipment_produced_carrier": {
    "description": "Total produced equipment of typecarrier"
  },
  "total_equipment_produced_missile_launcher": {
    "description": "Total produced equipment of typemissile_launcher"
  },
  "total_equipment_produced_": {
    "description": "Total produced equipment of type"
  },
  "total_equipment_produced_support": {
    "description": "Total produced equipment of typesupport"
  },
  "total_equipment_produced_amphibious": {
    "description": "Total produced equipment of typeamphibious"
  },
  "total_equipment_produced_anti_air": {
    "description": "Total produced equipment of typeanti_air"
  },
  "total_equipment_produced_artillery": {
    "description": "Total produced equipment of typeartillery"
  }
}

### state

{
  "distance_to": {
    "description": "distance to another state, uses target as another state. example: 123.distance_to@124"
  },
  "arms_factory_level": {
    "description": "military factory level in the state"
  },
  "non_damaged_building_level": {
    "description": "non damaged building level of a building with type, uses target as building type. example non_damaged_building_level@arms_factory"
  },
  "building_level": {
    "description": "building level of a building with type, uses target as building type. example building_level@arms_factory"
  },
  "owner": {
    "description": "owner of the state"
  },
  "industrial_complex_level": {
    "description": "civilian factor level in the state"
  },
  "infrastructure_level": {
    "description": "infrastructure level in the state"
  },
  "resistance_speed": {
    "description": "Compares the current resistance speed of a state to a value. Example: resistance_speed > 50 ",
    "is_trigger": true
  },
  "damaged_building_level": {
    "description": "damaged building level of a building with type, uses target as building type. example damaged_building_level@arms_factory"
  },
  "resistance_target": {
    "description": "Compares the target resistance level of a state to a value. Example: resistance_target > 50 ",
    "is_trigger": true
  },
  "modifier": {
    "description": "value of modifier stored in this state, uses target as modifier token, example: 123.modifier@local_manpower"
  },
  "core_countries": {
    "description": "countries that cores the state"
  },
  "state_and_terrain_strategic_value": {
    "description": "Checks for state strategic value",
    "is_trigger": true
  },
  "resource": {
    "description": "resources produced in state. example resource@steel"
  },
  "controller": {
    "description": "controller of the state"
  },
  "resistance": {
    "description": "Compares the current resistance level of a state to a value. Example: resistance > 50 ",
    "is_trigger": true
  },
  "state_population": {
    "description": "check the population in the state",
    "is_trigger": true
  },
  "state_strategic_value": {
    "description": "Checks for state strategic value",
    "is_trigger": true
  },
  "state_population_k": {
    "description": "check the population in the state in thousands (use to avoid variable overflows)",
    "is_trigger": true
  },
  "days_since_last_strategic_bombing": {
    "description": "Checks the days since last strategic bombing.\ndays_since_last_strategic_bombing < 10\n",
    "is_trigger": true
  },
  "compliance_speed": {
    "description": "Compares the current compliance speed of a state to a value. Example: compliance_speed > 50 ",
    "is_trigger": true
  },
  "compliance": {
    "description": "Compares the current compliance level of a state to a value. Example: compliance > 50 ",
    "is_trigger": true
  }
}

### unit_leader

{
  "num_battalions": {
    "description": "number of battalions"
  },
  "num_motorized": {
    "description": "number of units with motorized dominant type"
  },
  "num_units": {
    "description": "number of units controlled by leader"
  },
  "num_units_defensive_combats_on": {
    "description": "number of units that are defensively fighting on a terrain, terrain type is defined as target. example: num_units_defensive_combats_on@plains"
  },
  "state_deployed": {
    "description": "state ID where the general's deployed HQ is currently located; 0 if the general is not deployed or the HQ is not in a state (e.g. at sea)"
  },
  "planning_level": {
    "description": "planning level of the leader"
  },
  "has_orders_group": {
    "description": "1 if leader has orders group, zero otherwise"
  },
  "num_units_in_state": {
    "description": "number of units controlled by leader in state, state is in target. example num_units_in_state@123"
  },
  "province_deployed": {
    "description": "province ID where the general's deployed HQ is currently located; 0 if the general is not deployed"
  },
  "num_equipment": {
    "description": "number of equipment in army of a leader, equipment type token is defined in target. example num_equipment@infantry_equipment"
  },
  "num_cavalry": {
    "description": "number of units with cavalry dominant type"
  },
  "num_target_equipment": {
    "description": "number of equipment required in army of a leader, equipment type token is defined in target. example num_target_equipment@infantry_equipment"
  },
  "logistics_level": {
    "description": "logistics level of the leader"
  },
  "num_ships_with_type": {
    "description": "number of ships controlled by leader, ship type is defined in target. example num_ships_with_type@carrier"
  },
  "num_ships": {
    "description": "number of ships controlled by leader"
  },
  "num_battalions_with_type": {
    "description": "number of battalions with sub unit type, sub unit type is defined in target. example: num_battalions_with_type@light_armor"
  },
  "num_units_with_type": {
    "description": "number of units with dominant type controlled by leader, dominant type is defined in target. example: num_units_with_type@light_armor"
  },
  "num_units_on_climate": {
    "description": "number of units that are on an acclimatization required location, acclimatization type is defined in target. example num_units_on_climate@hot_climate"
  },
  "num_battle_plans": {
    "description": "number of battle plans of unit leader"
  },
  "num_infantry": {
    "description": "number of units with infantry dominant type"
  },
  "num_armored": {
    "description": "number of units with armored dominant type"
  },
  "num_artillery": {
    "description": "number of units with artillery dominant type"
  },
  "unit_ratio_ready_for_plan": {
    "description": "ratio of units that are ready for plan"
  },
  "num_units_defensive_combats": {
    "description": "number of units in defensive combats"
  },
  "num_special": {
    "description": "number of units with special dominant type"
  },
  "num_mechanized": {
    "description": "number of units with mechanized dominant type"
  },
  "num_assigned_traits": {
    "description": "number of assigned traits the leader has"
  },
  "num_rocket": {
    "description": "number of units with rocket dominant type"
  },
  "own_harmed_time_factor": {
    "description": "The time factor applied to the status \"harmed\". Takes int accountthe country it is operating for and the country it is operating against."
  },
  "num_traits": {
    "description": "number of traits a leader has"
  },
  "num_personality_traits": {
    "description": "number of personality traits a leader has"
  },
  "num_status_traits": {
    "description": "number of status traits a leader has"
  },
  "num_terrain_traits": {
    "description": "number of terrain traits a leader has"
  },
  "operation_type": {
    "description": "returns the operation token the operative is assigned"
  },
  "avg_unit_entrenchment_ratio": {
    "description": "average entrenchment ratio of all units"
  },
  "num_max_traits": {
    "description": "number of maximum assignable traits a leader can have"
  },
  "intel_yield_factor_on_capture": {
    "description": "Rate at which intel is extracted from this operative by an enemy country."
  },
  "num_basic_traits": {
    "description": "number of basic traits a leader has"
  },
  "skill_level": {
    "description": "skill level of the leader"
  },
  "army_attack_level": {
    "description": "attack level of the leader"
  },
  "attack_level": {
    "description": "attack level of the leader"
  },
  "army_defense_level": {
    "description": "defense level of the leader"
  },
  "avg_units_acclimation": {
    "description": "average unit acclimatization for a specific climate, acclimatization type is defined in target. example avg_units_acclimation@cold_climate"
  },
  "defense_level": {
    "description": "defense level of the leader"
  },
  "maneuvering_level": {
    "description": "maneuvering level of the leader"
  },
  "coordination_level": {
    "description": "coordination level of the leader"
  },
  "average_stats": {
    "description": "average stats of unit leader"
  },
  "sum_unit_terrain_modifier": {
    "description": "sum of terrain modifiers of each army's location, terrain type is defined in target. example: sum_unit_terrain_modifier@sickness_chance "
  },
  "leader_modifier": {
    "description": "value of a modifier stored in leader modifier, modifier token is defined in target. example leader_modifier@navy_max_range"
  },
  "unit_modifier": {
    "description": "value of a modifier stored in unit modifier, modifier token is defined in target. example unit_modifier@army_attack_factor"
  },
  "operation_state": {
    "description": "the state location the operative is assigned. 0 if it is not assigned to a state"
  },
  "num_units_in_combat": {
    "description": "number of units current fighting"
  },
  "avg_defensive_combat_status": {
    "description": "average progress of defensive combats"
  },
  "operation_country": {
    "description": "the country location the operative is assigned. 0 if it is not assigned to a country"
  },
  "avg_combat_status": {
    "description": "average progress of all combats"
  },
  "avg_offensive_combat_status": {
    "description": "average progress of offensive combats"
  },
  "num_units_crossing_river": {
    "description": "number of units currently passing through a river"
  },
  "num_units_offensive_combats": {
    "description": "number of units in offensive combats"
  },
  "avg_unit_planning_ratio": {
    "description": "average planning ratio of all units"
  },
  "num_units_offensive_combats_against": {
    "description": "number of units that are offensively fighting against a terrain, terrain type is defined as target. example: num_units_offensive_combats_against@plains"
  },
  "own_capture_chance_factor": {
    "description": "The chance this operative has to be captured, taking into account the country it is operating for and the country it is operating against."
  },
  "own_forced_into_hiding_time_factor": {
    "description": "The time factor applied to the status \"forced into hiding\". Takes into account the country it is operating for and the country it is operating against."
  },
  "operative_captor": {
    "description": "returns the country tag that captured the operative"
  },
  "skill": {
    "description": "compare leader skill levels",
    "is_trigger": true
  },
  "attack_skill_level": {
    "description": "Compares attack skill level of a unit leader.\nExample: attack_skill_level > 5",
    "is_trigger": true
  },
  "defense_skill_level": {
    "description": "Compares defense skill level of a unit leader.\nExample: defense_skill_level > 5",
    "is_trigger": true
  },
  "logistics_skill_level": {
    "description": "Compares logistics skill level of a unit leader.\nExample: logistics_skill_level > 5",
    "is_trigger": true
  },
  "planning_skill_level": {
    "description": "Compares planning skill level of a unit leader.\nExample: planning_skill_level > 5",
    "is_trigger": true
  }
}

### military_industrial_organization

{
  "max_task_capacity": {
    "description": "Maximum task capacity of the military industrial organization."
  },
  "number_of_unlocked_traits": {
    "description": "Number of unlocked traits of the military industrial organization."
  },
  "size": {
    "description": "Size of the military industrial organization"
  },
  "number_of_currently_assigned_tasks": {
    "description": "Number of tasks the military industrial organization is currently assigned to"
  },
  "funds": {
    "description": "Funds of the military industrial organization"
  },
  "number_of_unused_trait_points": {
    "description": "Number of unused trait points of the military industrial organization"
  },
  "modifier": {
    "description": "Value of the modifier stored in the military industrial organization.\nex: modifier@military_industrial_organization_research_bonus"
  },
  "research_bonus": {
    "description": "Research bonus of the military industrial organization when assigned to a research slot"
  }
}

### special_project

{
  "facility_state": {
    "description": "State that the project is researched in"
  },
  "facility_province_id": {
    "description": "The province that the project is researched in"
  },
  "scientist": {
    "description": "The scientist that researches the project"
  }
}

## console_commands

### commands

{
  "rendertype": {
    "description": "Reports what render backend is used"
  },
  "CrashReporter.SimulateCrash": {
    "description": "Simulates a crash (resulting in the game exiting)."
  },
  "CrashReporter.DeleteCrashData": {
    "description": "Delete local crash dumps older than X days."
  },
  "test": {
    "available_in_release_build": false,
    "description": "This is a placeholder command. Use it for your debug code if you need to quickly test something locally. Or copy and paste it to create a new console command."
  },
  "faction_initiative": {
    "arguments": [
      "amount",
      "countrytag"
    ],
    "aliases": [
      "fi"
    ],
    "description": "Adds faction initiative to the country, on default it takes the player country if no tag is provided"
  },
  "faction_unlock": {
    "arguments": [
      "type"
    ],
    "aliases": [
      "fu"
    ],
    "description": "Unlocks a part of the faction, can take the argument military (m) or research (r)"
  },
  "faction_goal_slot": {
    "arguments": [
      "category",
      "amount"
    ],
    "aliases": [
      "fgs"
    ],
    "description": "Adds a faction goal slot, categories are short medium long"
  },
  "faction_influence": {
    "arguments": [
      "amount",
      "countrytag"
    ],
    "aliases": [
      "finf"
    ],
    "description": "Adds faction influence (stored) to the country, on default it takes the player country if no tag is provided"
  },
  "toggle_silhouette_portraits": {
    "available_in_release_build": false,
    "description": "Enables and disables silhouette portraits."
  },
  "add_mines": {
    "arguments": [
      "<Amount of naval mines>"
    ],
    "aliases": [
      "mines"
    ],
    "description": "Add naval mines to selected region(s)"
  },
  "release": {
    "arguments": [
      "Tag of a country to be released"
    ],
    "aliases": [
      "rls"
    ],
    "description": "Released a given country"
  },
  "map_icon_reload_type": {
    "available_in_release_build": false,
    "arguments": [
      "<NUM> or <help>"
    ],
    "description": "Specify a map icon type to reload"
  },
  "randomlog": {
    "available_in_release_build": false,
    "aliases": [
      "rlog"
    ],
    "description": "Toggles the random logs."
  },
  "oos_dump": {
    "available_in_release_build": false,
    "aliases": [
      "oosdump"
    ],
    "description": "Generates an oos dump on demand for local client."
  },
  "acclimatization": {
    "arguments": [
      "<climate_name>",
      "<value 0-100>"
    ],
    "aliases": [
      "acc"
    ],
    "description": "Sets the acclimatization on a division(s)."
  },
  "combattest": {
    "available_in_release_build": false,
    "description": "combat simulation process"
  },
  "navalcombatlog": {
    "available_in_release_build": false,
    "description": "logs naval combat"
  },
  "debug": {
    "description": "Toggle debug mode on/off."
  },
  "deironman": {
    "available_in_release_build": false,
    "description": "Removes Ironman status from current game."
  },
  "show_xp_gain": {
    "aliases": [
      "xp_gain"
    ],
    "description": "Show XP gain information."
  },
  "whitepeace": {
    "arguments": [
      "<country tags>"
    ],
    "aliases": [
      "wp"
    ],
    "description": "White peace with the specified countries."
  },
  "debug_orders_tree": {
    "available_in_release_build": false,
    "aliases": [
      "dot"
    ],
    "description": "Print out debug about orders chain."
  },
  "testtool": {
    "available_in_release_build": false,
    "description": "Testing tool."
  },
  "analyzetheatres": {
    "aliases": [
      "anth"
    ],
    "description": "Analyze theatres for errors."
  },
  "debug_front_sections": {
    "arguments": [
      "<Theatre index>",
      "<Front index>",
      "<Section index>"
    ],
    "aliases": [
      "dbg_fs"
    ],
    "description": "Visual debug of theatres, fronts and sections."
  },
  "rebuildfronts": {
    "available_in_release_build": false,
    "arguments": [
      "<Country tag>"
    ],
    "description": "Rebuild fronts."
  },
  "debug_unit_controller_weights": {
    "arguments": [
      "<weight token>"
    ],
    "aliases": [
      "dbg_ucw"
    ],
    "description": "Visual debug of unit controller weights. Enable track_unit_controller_weights first!"
  },
  "track_unit_controller_weights": {
    "aliases": [
      "track_ucw"
    ],
    "description": "Will start tracking unit controller weights for current country, should be used together with debug_unit_controller_weights to view the data."
  },
  "debug_force_capitulate": {
    "arguments": [
      "<tag>"
    ],
    "aliases": [
      "dfc"
    ],
    "description": "forces capitulation of a country on next daily tick"
  },
  "massconquer": {
    "available_in_release_build": false,
    "aliases": [
      "massc"
    ],
    "description": "Mass conquer tool."
  },
  "deleteallunits": {
    "aliases": [
      "delall"
    ],
    "description": "Delete all armies and fleets of the specified countries."
  },
  "deleteallunitsbut": {
    "aliases": [
      "delallbut"
    ],
    "description": "Delete all armies and fleets of ALL countries, except specified one."
  },
  "aircombat": {
    "available_in_release_build": false,
    "arguments": [
      "<scenario name>",
      "<result name>",
      "<province id>",
      "<state id with airbase>",
      "<state id with airbase>",
      "<equipment type>",
      "<equipment type>",
      "[equipment creator country]",
      "[equipment creator country]"
    ],
    "aliases": [
      "airc"
    ],
    "description": "Spawns an air combat in desired location."
  },
  "teleport": {
    "arguments": [
      "<province_id>"
    ],
    "aliases": [
      "tp"
    ],
    "description": "Teleports selected armies or ships to the specified province"
  },
  "theatersrebuild": {
    "available_in_release_build": false,
    "aliases": [
      "trebuild"
    ],
    "description": "Rebuilds all theatres in the world. All orders will be cleaned."
  },
  "test_naval_move_danger": {
    "available_in_release_build": false,
    "arguments": [
      "<from region id>",
      "<to region id>"
    ],
    "description": "Tests if path between two regions is blocked for surface warships"
  },
  "highlight_encirclements": {
    "description": "Toggle highlighting of detected encirclements"
  },
  "simplified_transport": {
    "description": "Toggle simplified naval transports"
  },
  "fronts": {
    "description": "Toggle visibility of the foreign fronts"
  },
  "traderoutes": {
    "description": "Toggle visibility of trade routes"
  },
  "railroads": {
    "description": "Toggle rendering of railroads"
  },
  "debug_norender": {
    "description": "Toggle rendering of map"
  },
  "debug_tactics": {
    "description": "Toggle visibility of debug tooltip for tactics"
  },
  "show_ships": {
    "description": "Toggle always showing of player ships"
  },
  "show_enemy_ships": {
    "description": "Toggle always showing of enemy ships"
  },
  "allowdiplo": {
    "aliases": [
      "adiplo",
      "nocb"
    ],
    "description": "Allows to use all diplomatic actions for no matter the rules."
  },
  "allowtraits": {
    "description": "Allows to learn all traits."
  },
  "allowideas": {
    "description": "Allows to learn all ideas."
  },
  "allowoperations": {
    "description": "Allows to execute all operations."
  },
  "operation_test_phase_selection": {
    "arguments": [
      "Operation ID",
      "Target Tag"
    ],
    "description": "Test an operation phase."
  },
  "operation_debug": {
    "arguments": [
      "Operation ID",
      "Target Tag"
    ],
    "description": "Allows to execute all operations."
  },
  "operation_start": {
    "arguments": [
      "Operation ID",
      "Target Tag"
    ],
    "description": "Allows to execute all operations."
  },
  "nukes": {
    "arguments": [
      "<count>"
    ],
    "aliases": [
      "nuke"
    ],
    "description": "add nukes"
  },
  "launch_nuke": {
    "arguments": [
      "[Nuke Type]",
      "<Province ID>",
      "..."
    ],
    "aliases": [
      "ln"
    ],
    "description": "Launch nuke to any specified province(s) without checking any conditions."
  },
  "armageddon": {
    "description": "Deliver a thermonuclear strike to every state in the game."
  },
  "instantevents": {
    "description": "Ignores event mth s"
  },
  "rebuildlayers": {
    "description": "Reload mapmodes."
  },
  "deltat": {
    "arguments": [
      "<speed factor>"
    ],
    "description": "control animation speeds"
  },
  "building_health": {
    "arguments": [
      "<building type>",
      "<state or prov id>",
      "<building level>",
      "<health to add>"
    ],
    "aliases": [
      "bhealth"
    ],
    "description": "Changes specified building health"
  },
  "instantconstruction": {
    "aliases": [
      "ic"
    ],
    "description": "Toggles instant construction cheat."
  },
  "instantshiprefit": {
    "aliases": [
      "isr"
    ],
    "description": "Toggles instant ship refitting cheat."
  },
  "instanttraining": {
    "aliases": [
      "it"
    ],
    "description": "Toggles instant army training cheat."
  },
  "war_relations": {
    "arguments": [
      "<tag>"
    ],
    "description": "Prints war relations info"
  },
  "unit_stats": {
    "description": "lists stats of selected units"
  },
  "trigger_ability": {
    "arguments": [
      "<ability_name>"
    ],
    "description": "triggers an ability"
  },
  "profile": {
    "arguments": [
      "<on> <off> <print> <clear>"
    ],
    "description": "profile options"
  },
  "nomapicons": {
    "description": "Toggles map icons."
  },
  "nopausetext": {
    "description": "Toggles the pausebanner for nicer screenshots."
  },
  "time": {
    "description": "What time is it?"
  },
  "combatsound": {
    "description": "How often does the combat view give a random sound? 0-50"
  },
  "Audio.PlayEffect": {
    "arguments": [
      "effect_name"
    ],
    "description": "Play the specified sound effect"
  },
  "morehumans": {
    "arguments": [
      "num"
    ],
    "aliases": [
      "humans"
    ],
    "description": "Adds more humans"
  },
  "morehumanswithcountries": {
    "arguments": [
      "num"
    ],
    "description": "Adds more humans and assigns them to the highest scoring countries available"
  },
  "window": {
    "arguments": [
      "Arguments: open/close",
      "window gui name"
    ],
    "aliases": [
      "wnd"
    ],
    "description": "Opens or closes the specified window"
  },
  "reloadinterface": {
    "description": "Reloads the entire interface"
  },
  "reloadtechnologies": {
    "description": "Reloads the technology database"
  },
  "updateequipments": {
    "description": "Updates the equipment database"
  },
  "updatesubunits": {
    "description": "Updates the subunit database"
  },
  "reloadoob": {
    "arguments": [
      "<Target Country Tag>"
    ],
    "description": "Reloads OOBs"
  },
  "createarmygroup": {
    "description": "Create field marshal group from selected groups"
  },
  "combat_analyzer": {
    "arguments": [
      "<TAG1>",
      "<TAG2>",
      "<OOB1>",
      "<OOB2>",
      "<num runs> OPTIONAL",
      "<num days> OPTIONAL"
    ],
    "description": "Runs a combat between the 2 OOBs owned by the two TAGs either until done or for the specified number of days. \nUsing <num runs> the combat will be run multiple times and the averages are printed"
  },
  "reloadfx": {
    "arguments": [
      "Arguments: map/mapname/postfx or *.fx filename"
    ],
    "description": "Reloads the shader"
  },
  "update_loc": {
    "arguments": [
      "localization tag"
    ],
    "description": "Updates the localization tag file"
  },
  "event": {
    "arguments": [
      "event id",
      "<Target Country Tag>"
    ],
    "description": "Executes an event"
  },
  "research": {
    "arguments": [
      "<slot id> or \"all\""
    ],
    "description": "Researches an technology from research slot or all."
  },
  "research_on_icon_click": {
    "aliases": [
      "roic"
    ],
    "description": "Research a technology when clicking on technology tree icon"
  },
  "research_fast": {
    "description": "Base cost of every technology is set to 1 RP"
  },
  "Agency.Instant": {
    "description": "Activates Operation.Instant, IntelNetwork.Instant, Agency.InstantSlotUnlock and Agency.Autocomplete"
  },
  "add_autonomy": {},
  "annex": {
    "arguments": [
      "<Target Country Tag>"
    ],
    "description": "Begin annex/annexes the specified tag"
  },
  "puppet": {
    "arguments": [
      "<Target Country Tag>"
    ],
    "description": "Puppets the specified tag"
  },
  "focus_count": {
    "arguments": [
      "<Target Country Tag>"
    ],
    "description": "Counts how many focuses a tag has. For science"
  },
  "no_wargoal": {
    "description": "No need to have a wargoal for declaring war"
  },
  "instant_wargoal": {
    "description": "Generation of wargoals are instant"
  },
  "testrtti": {
    "arguments": [
      "<test case>"
    ],
    "description": "Tests performance for RTTI"
  },
  "testevent": {
    "arguments": [
      "<Event ID>",
      "<Character ID>"
    ],
    "description": "Tests an event without triggering it"
  },
  "manpower": {
    "arguments": [
      "<Amount>"
    ],
    "description": "Adds manpower to player"
  },
  "add_opinion": {
    "arguments": [
      "<Country tag>"
    ],
    "description": "Add opinion to/from tag"
  },
  "reduce_opinion": {
    "arguments": [
      "<Country tag>"
    ],
    "description": "Reduce opinion to/from tag"
  },
  "tag": {
    "arguments": [
      "<Country tag>"
    ],
    "description": "Switch tag to another country"
  },
  "resign": {
    "description": "Resign from the game"
  },
  "add_diplo": {
    "description": "Adds diplomatic entroute"
  },
  "build_war_blobs": {
    "description": "Prints a list of all your wars"
  },
  "PrintSynchStuff": {
    "description": "Prints random count and seed"
  },
  "SetRandomCount": {
    "description": "Sets the randomcount to 0 or arg"
  },
  "observe": {
    "aliases": [
      "spectator"
    ],
    "description": "Switches to play no country at all, and no longer shows messages or pauses the game"
  },
  "lock_air_det": {
    "arguments": [
      "<CountryTag>",
      "<Detection> (0.0-1.0) OPTIONAL"
    ],
    "description": "Locks Air Detection for a country, omit detection value to reset"
  },
  "lock_air_eff": {
    "arguments": [
      "<CountryTag>",
      "<Efficiency> (0.0-1.0) OPTIONAL"
    ],
    "description": "Locks Air Efficiency for a country, omit efficiency value to reset"
  },
  "ai_trace": {
    "available_in_release_build": false,
    "description": "Toggles the AI Trace window"
  },
  "ai": {
    "description": "Toggles the AI on or off"
  },
  "enable_ai": {
    "description": "Enables the AI"
  },
  "disable_ai": {
    "description": "Disables the AI"
  },
  "human_ai": {
    "description": "Toggles AI for Human countries"
  },
  "ai_invasion": {
    "description": "Toggles AI AI naval invasions"
  },
  "ai_accept": {
    "aliases": [
      "yesman"
    ],
    "description": "Toggles AI always accept diplomacy"
  },
  "fow": {
    "arguments": [
      "<Province ID> OPTIONAL"
    ],
    "aliases": [
      "debug_fow"
    ],
    "description": "Turns off fog of war in a province or in general"
  },
  "collision": {
    "aliases": [
      "debug_collision"
    ],
    "description": "Toggles debug display of normals/bounding boxes/collision"
  },
  "savegame": {
    "aliases": [
      "save"
    ],
    "description": "Creates a save file."
  },
  "savecheck": {
    "description": "Makes a savegame (Test_01), loads the savegame, makes a new savegame (Test_02). Those savegames should look the same."
  },
  "IP": {
    "description": "Shows your IP"
  },
  "nudge": {
    "description": "Go to the nudge tool"
  },
  "mapmode": {
    "arguments": [
      "Mapmode type (int)"
    ],
    "description": "Change mapmode."
  },
  "fullscreen": {
    "description": "Toggles fullscreen"
  },
  "prices": {
    "description": "Price Info"
  },
  "add_core": {
    "arguments": [
      "<Province ID>"
    ],
    "description": "Add core"
  },
  "remove_core": {
    "arguments": [
      "<Province ID>"
    ],
    "description": "Remove core"
  },
  "debug_zoom": {
    "description": "Zooms in the game"
  },
  "debug_types": {
    "available_in_release_build": false,
    "description": "Will print the data type for all dynamic reference objects. Can only be used if using RTTI."
  },
  "debug_show_event_ID": {
    "description": "Shows event ID"
  },
  "debug_events": {
    "description": "Start Counting events"
  },
  "dump_garrison_templates": {
    "description": "Dump garrison templates to game log"
  },
  "debug_dumpevents": {
    "description": "Dump Event data to game log"
  },
  "dump_cached_random_logs": {
    "description": "dumps cached random logs"
  },
  "debug_diploactions": {
    "available_in_release_build": false,
    "description": "Start Counting diplomatic actions"
  },
  "debug_dumpdiploactions": {
    "available_in_release_build": false,
    "description": "Dump diplomatic action data to game log"
  },
  "debug_checkportraitssanity": {
    "description": "Analyse all characters' portraits and write failures in error log"
  },
  "debug_assert": {
    "available_in_release_build": false,
    "description": "Toggles asserts on/off"
  },
  "debug_smooth": {
    "description": "Toggle framesmoothing"
  },
  "debug_nomouse": {
    "description": "Toggles mouse scrollwheel on/off"
  },
  "debug_terrain": {
    "description": "Toggles Terrain on/off"
  },
  "debug_cities": {
    "description": "Toggles Cities painting mode on/off"
  },
  "debug_water": {
    "description": "Toggles Water on/off"
  },
  "debug_fronts": {
    "available_in_release_build": false,
    "description": "Toggles interpolated fronts debug"
  },
  "history_logger": {
    "description": "Toggle history logger"
  },
  "instant_prepare": {
    "description": "Instantly prepares naval invasions"
  },
  "debug_off_front_snap": {
    "available_in_release_build": false,
    "aliases": [
      "dbg_fsnap"
    ],
    "description": "Toggles offensive fronts snapping debug"
  },
  "debug_borders": {
    "description": "Toggles Borders on/off"
  },
  "debug_trees": {
    "description": "Toggles Trees on/off"
  },
  "debug_rivers": {
    "description": "Toggles Rivers on/off"
  },
  "debug_postfx": {
    "description": "Toggles PostFX on/off"
  },
  "debug_sky": {
    "description": "Toggles Sky on/off"
  },
  "debug_bloom": {
    "description": "Toggles Bloom on/off"
  },
  "debug_tooltip": {
    "description": "Toggles Tooltips on/off"
  },
  "flagsoutput": {
    "arguments": [
      "<path>"
    ],
    "description": "Creates texture atlas files from memory."
  },
  "cityreload": {
    "description": "Reloads the cities"
  },
  "error": {
    "description": "Show errors in log"
  },
  "version": {
    "description": "Show current game version"
  },
  "debug_nogui": {
    "description": "Toggles GUI on/off"
  },
  "debug_lockcamera": {
    "description": "Toggles Camera locked on/off"
  },
  "debug_lines": {
    "available_in_release_build": false,
    "description": "Toggles Debuglines"
  },
  "debug_entities": {
    "available_in_release_build": false,
    "description": "Toggles Debug entities"
  },
  "debug_info": {
    "available_in_release_build": false,
    "description": "Toggles Debug info"
  },
  "debug_particle": {
    "available_in_release_build": false,
    "description": "Toggles Particles Debug info"
  },
  "debug_textures": {
    "available_in_release_build": false,
    "description": "Writes Texture info to application debug log"
  },
  "reload_textures": {
    "arguments": [
      "<optional file name filters...>"
    ],
    "aliases": [
      "rt",
      "reload_texture"
    ],
    "description": "Reloads all textures, with an optional filter to reload only files that include the given text"
  },
  "debug_texture": {
    "available_in_release_build": false,
    "description": "draws textures like bloom"
  },
  "debug_wireframe": {
    "available_in_release_build": false,
    "description": "Toggles forced wireframe on/off"
  },
  "debug_achievements_clear": {
    "available_in_release_build": false,
    "description": "Clear all achievements and user stats"
  },
  "debug_achievements": {
    "available_in_release_build": false,
    "description": "Enables popups for achievements to debug them"
  },
  "debug_custom_achievements": {
    "description": "For testing custom achievements, clear completion status (delete files on cloud storage) and reload mod achievement files"
  },
  "moveunit": {
    "arguments": [
      "<Unit ID>",
      "<Province ID>"
    ],
    "description": "Moves a unit to a province"
  },
  "spawnactor": {
    "arguments": [
      "<Actorname>",
      "<Province ID>",
      "<Animation> OPTIONAL"
    ],
    "description": "Spawns an actor with an optional animation"
  },
  "spawn": {
    "available_in_release_build": false,
    "arguments": [
      "<SubUnit Type>",
      "<Province ID>",
      "<Amount>"
    ],
    "description": "Spawns a unit in a province"
  },
  "guibounds": {
    "aliases": [
      "gui"
    ],
    "description": "Toggles GUI bounds debug"
  },
  "cameraclamp": {
    "description": "Toggles the camera clamping"
  },
  "provtooltipdebug": {
    "aliases": [
      "tdebug"
    ],
    "description": "Toggles the debug info in province tooltip"
  },
  "reloadweather": {
    "arguments": [
      "<randomseed>"
    ],
    "description": "Reload and regenerate weather"
  },
  "weather": {
    "description": "Toggle weather simulation"
  },
  "enable_weather": {
    "description": "Enable weather simulation"
  },
  "disable_weather": {
    "description": "Disable weather simulation"
  },
  "debug_air_vs_land": {
    "available_in_release_build": false,
    "aliases": [
      "dbg_cas"
    ],
    "description": "Toggle debug mode for air vs land combat."
  },
  "supply_toggle_flow_penalties": {
    "available_in_release_build": false,
    "description": "Toggle the supply penalties due to bad supply flow"
  },
  "finish_decision": {
    "arguments": [
      "<decision id> or \"all\""
    ],
    "description": "Finish timed missions instantly"
  },
  "add_temp_supply_node": {
    "available_in_release_build": false,
    "description": "Add temp supply node"
  },
  "mapnames": {
    "description": "Toggle map names"
  },
  "gbreload": {
    "available_in_release_build": false,
    "description": "Reloads gradient borders"
  },
  "gbpaint": {
    "available_in_release_build": false,
    "arguments": [
      "layer",
      "channel"
    ],
    "description": "Toggles gradient border painting"
  },
  "occupationpaint": {
    "arguments": [
      "tag<OPTIONAL>"
    ],
    "aliases": [
      "op"
    ],
    "description": "Toggles occupation painting. If specifying a tag, that country will be occupied."
  },
  "setowner": {
    "arguments": [
      "country tag",
      "state id"
    ],
    "description": "Sets state owner"
  },
  "setcontroller": {
    "arguments": [
      "country tag",
      "province id"
    ],
    "description": "Sets province controller"
  },
  "gamestate_timer": {
    "arguments": [
      "on / off"
    ],
    "aliases": [
      "gstimer"
    ],
    "description": "Enable / Disable recording of how long an hour / day / week etc takes to process."
  },
  "run": {
    "description": "Runs the specified file with list of commands"
  },
  "oos": {
    "available_in_release_build": false,
    "description": "Out of Synch"
  },
  "debug_crash": {
    "available_in_release_build": false,
    "aliases": [
      "crash"
    ],
    "description": "Crash!"
  },
  "debug_unit_entity": {
    "aliases": [
      "dbg_ue"
    ],
    "description": "Print out the entity hierarchy."
  },
  "sleep": {
    "available_in_release_build": false,
    "arguments": [
      "time in sec"
    ],
    "aliases": [
      "wait"
    ],
    "description": "Sleep"
  },
  "goto_province": {
    "arguments": [
      "province id"
    ],
    "description": "Centers to province"
  },
  "goto_state": {
    "arguments": [
      "state id"
    ],
    "description": "Centers to state"
  },
  "goto_region": {
    "arguments": [
      "region id"
    ],
    "description": "Centers to region"
  },
  "show_focuses": {
    "description": "shows all the hidden focuses"
  },
  "list_hidden_focuses": {
    "arguments": [
      "country tag"
    ],
    "aliases": [
      "list_hd"
    ],
    "description": "lists all of the hidden focuses from a country"
  },
  "trigger_docs": {
    "aliases": [
      "effect_docs",
      "scripting_docs",
      "docs"
    ],
    "description": "Print docs for triggers, effects and variables"
  },
  "cp": {
    "arguments": [
      "CP amount"
    ],
    "description": "Gives command power to player"
  },
  "effect": {
    "arguments": [
      "<tag> scripted_effect_name"
    ],
    "aliases": [
      "e"
    ],
    "description": "Runs a scripted effect on selected scope",
    "argument_completion_support": true
  },
  "eval_effect": {
    "description": "Runs the inlined effect on a selected scope"
  },
  "eval_trigger": {
    "description": "Runs the inlined trigger on a selected scope"
  },
  "trigger": {
    "arguments": [
      "<tag> scripted_trigger_name"
    ],
    "aliases": [
      "t"
    ],
    "description": "Runs a scripted trigger on selected scope",
    "argument_completion_support": true
  },
  "print_operation_tokens": {
    "description": "Runs a scripted effect on selected scope"
  },
  "xp": {
    "arguments": [
      "XP amount"
    ],
    "description": "Gives Army, navy and air experience to player"
  },
  "threat": {
    "arguments": [
      "threat amount"
    ],
    "aliases": [
      "tension"
    ],
    "description": "Adds or show threat level of player"
  },
  "add_latest_equipment": {
    "arguments": [
      "equipment amount"
    ],
    "aliases": [
      "ale"
    ],
    "description": "Gives player amount of latest equipment variants"
  },
  "add_equipment": {
    "arguments": [
      "equipment amount",
      "equipment name"
    ],
    "aliases": [
      "ae"
    ],
    "description": "Gives player amount of equipment that has the specified name"
  },
  "pp": {
    "arguments": [
      "PP amount"
    ],
    "aliases": [
      "political_power"
    ],
    "description": "Gives political power to player"
  },
  "fuel": {
    "arguments": [
      "Fuel amount"
    ],
    "aliases": [
      "army_juice"
    ],
    "description": "Adds/removes fuel to the player"
  },
  "fuel_gain": {
    "arguments": [
      "Daily Fuel amount"
    ],
    "description": "Adds/removes daily fuel gain for player"
  },
  "empty_fuel_tanks": {
    "arguments": [
      "Fuel amount"
    ],
    "description": "Clear fuel tanks of all armies"
  },
  "resistance": {
    "arguments": [
      "amount"
    ],
    "description": "increases decreases resistance in a state"
  },
  "compliance": {
    "arguments": [
      "amount"
    ],
    "description": "increases decreases compliance in a state"
  },
  "add_stability": {
    "arguments": [
      "unity amount"
    ],
    "aliases": [
      "st"
    ],
    "description": "Gives/removes stability from player"
  },
  "add_war_support": {
    "arguments": [
      "unity amount"
    ],
    "aliases": [
      "ws"
    ],
    "description": "Gives/removes war support from player"
  },
  "3dstats": {
    "description": "Toggles 3D Stats"
  },
  "hdr": {
    "available_in_release_build": false,
    "description": "Toggles hdr"
  },
  "hdr_debug": {
    "available_in_release_build": false,
    "description": "Toggles hdr debugging"
  },
  "srgb": {
    "available_in_release_build": false,
    "description": "Toggles sRGB"
  },
  "bloom": {
    "available_in_release_build": false,
    "description": "Toggles bloom"
  },
  "PostEffectVolumes.Default": {
    "available_in_release_build": false,
    "arguments": [
      "posteffect_values name"
    ],
    "description": "Toggles default posteffect values"
  },
  "night": {
    "available_in_release_build": false,
    "description": "Toggles night"
  },
  "civilwar": {
    "arguments": [
      "<ideology>",
      "[target country tag]"
    ],
    "description": "Spawns a civil war",
    "argument_completion_support": true
  },
  "createlean": {
    "available_in_release_build": false,
    "description": "Create LEAN textures"
  },
  "helplog": {
    "description": "Print out all console commands to game.log file."
  },
  "help": {
    "arguments": [
      "command name"
    ],
    "description": "Print out all console commands or a specific command description."
  },
  "helphelp": {
    "description": "Double Rainbow help."
  },
  "hsv": {
    "available_in_release_build": false,
    "description": "Converts RGB to HSV"
  },
  "tag_color": {
    "description": "Test setting a country's color"
  },
  "browser": {
    "available_in_release_build": false,
    "arguments": [
      "url"
    ],
    "description": "Show browser window"
  },
  "aiview": {
    "description": "Enable AI debug info"
  },
  "ai_dump": {
    "available_in_release_build": false,
    "aliases": [
      "aidump"
    ],
    "description": "Dump AI data to log file"
  },
  "ai_front_dump": {
    "available_in_release_build": false,
    "aliases": [
      "aifrontdump"
    ],
    "description": "Dump AI front data to log file, needs to have a unit selected"
  },
  "metrics": {
    "available_in_release_build": false,
    "arguments": [
      "log_units|log_pools|player|air_mission|global|unit_assignments <days>|decision|log|file<=file_name>|tag=<country_tag>|add_tag=<country_tag>"
    ],
    "description": "Toggles collecting metrics"
  },
  "ai_research_log": {
    "available_in_release_build": false,
    "description": "Toggles ai research logging"
  },
  "ai_idea_desire_log": {
    "description": "Prints AI desire for ideas to log. For Current country only."
  },
  "set_debug_unit_controller": {
    "available_in_release_build": false,
    "aliases": [
      "dbg_unit_controller"
    ],
    "description": "Sets debug unit controller tag, other countries will not update units"
  },
  "ai_pp_log": {
    "description": "Prints AI use of PP to log"
  },
  "airealism": {
    "description": "Enable realistic AI"
  },
  "ai_force_template": {
    "description": "Force the AI to only spend army XP on template design"
  },
  "ai_force_equipment": {
    "description": "Force the AI to only spend army XP on equipment design"
  },
  "pause_on_trigger": {
    "description": "Pauses the game when trigger activates",
    "argument_completion_support": true
  },
  "pause_in_hours": {
    "description": "Pauses the game after X hours have passed after command is called"
  },
  "pathfind_stats": {
    "available_in_release_build": false,
    "description": "Print PathFind Cache Stats"
  },
  "debug_army_entity": {
    "aliases": [
      "dae"
    ],
    "description": "Shows debug entity for all armies"
  },
  "fast_forward": {
    "arguments": [
      "<amount of days>",
      "<observer>"
    ],
    "description": "Fast forward a set amount of days"
  },
  "pathfind_cache": {
    "available_in_release_build": false,
    "arguments": [
      "on / off"
    ],
    "description": "Enable / Disable the PathFind Cache"
  },
  "gamespeed": {
    "arguments": [
      "speed <0-5>"
    ],
    "description": "Set the current game speed, pausing the game at speed 0."
  },
  "unit_address": {
    "description": "Get the address of the first selected unit, for debugging"
  },
  "ai_front_id": {
    "description": "Get the address of selected group's front debug id"
  },
  "test_log": {
    "description": "Enable / Disable tests"
  },
  "test_save_mode": {
    "description": "Sets if save game for failed test should be for current or previous day"
  },
  "set_cosmetic_tag": {
    "arguments": [
      "<country tag>",
      "<cosmetic tag>"
    ],
    "description": "Sets 'cosmetic tag' for a specified country"
  },
  "drop_cosmetic_tag": {
    "arguments": [
      "<country tag>"
    ],
    "description": "Drops 'cosmetic tag' for a specified country"
  },
  "add_ideas": {
    "arguments": [
      "all|<idea1> <idea2> ...>"
    ],
    "description": "Adds ideas (ministers or national spirits) with <ID> to the country. Use 'all' to add them all",
    "argument_completion_support": true
  },
  "remove_ideas": {
    "arguments": [
      "all|<idea1> <idea2> ..."
    ],
    "description": "Removes ideas (ministers or national spirits) with <ID> to the country. Use 'all' to remove them all",
    "argument_completion_support": true
  },
  "list_ideas": {
    "description": "Dump all ideas to console (ministers or national spirits)"
  },
  "add_party_popularity": {
    "arguments": [
      "<party>",
      "<amount>"
    ],
    "description": "Adds party popularity for specified party to the current country"
  },
  "set_ruling_party": {
    "arguments": [
      "<ideology>"
    ],
    "description": "Sets ruling party for the country"
  },
  "set_global_flag": {
    "arguments": [
      "<flag name>"
    ],
    "description": "Sets the specified global flag to a value. Defaults to 1"
  },
  "set_country_flag": {
    "arguments": [
      "<flag name>"
    ],
    "description": "Sets country flag on specified TAG for a duration. Defaults to current country and value 1 with infinite duration."
  },
  "get_country_flag": {
    "arguments": [
      "<flag name>"
    ],
    "description": "Gets country flag on specified TAG. Defaults to current country"
  },
  "set_var": {
    "arguments": [
      "<var name>"
    ],
    "description": "Set a variable"
  },
  "get_var": {
    "arguments": [
      "<var name>"
    ],
    "description": "Gets a variable"
  },
  "set_flag": {
    "arguments": [
      "<flag name>"
    ],
    "description": "Set a flag"
  },
  "get_flag": {
    "arguments": [
      "<flag name>"
    ],
    "description": "Get a flag"
  },
  "list_vars": {
    "arguments": [
      "<scope>"
    ],
    "description": "Lists all variables in a scope or for the selected country/state/unitleader"
  },
  "gain_xp": {
    "arguments": [
      "<trait>"
    ],
    "description": "Gain xp for selected leader or for a leader trait"
  },
  "capture_commander": {
    "arguments": [
      "<owner_tag>",
      "<leader>"
    ],
    "description": "Capture an enemy commander for the player country. <province_id> is required if the commander is not deployed."
  },
  "list_flags": {
    "arguments": [
      "<scope>"
    ],
    "description": "Lists all flags in a scope or for the selected country/state/unitleader"
  },
  "list_modifiers": {
    "arguments": [
      "<scope>"
    ],
    "description": "Lists all modifiers in a scope or for the selected country/state/unitleader"
  },
  "list_leader_modifiers": {
    "description": "Lists the leader and unit modifiers on the leader of each selected army"
  },
  "dbg_enable_scripted_gui": {
    "available_in_release_build": false,
    "arguments": [
      "<scope>"
    ],
    "description": "Enables scripted GUIs"
  },
  "prep_for_war": {
    "arguments": [
      "<TAG>"
    ],
    "description": "Make AI country with specified TAG to prepare fight for another country "
  },
  "dbg_prov": {
    "available_in_release_build": false,
    "arguments": [
      "<int>"
    ],
    "description": "Sets type of debugging information on provinces."
  },
  "random_seed": {
    "description": "reseeds random with specified seed or reseeds random"
  },
  "timer": {
    "description": "Prints out debug timing info"
  },
  "timer_start": {
    "description": "Starts debug timing"
  },
  "timer_restart": {
    "description": "Restarts (resets and starts) debug timing"
  },
  "timer_reset": {
    "description": "Resets debug timing"
  },
  "timer_stop": {
    "description": "Stops debug timing"
  },
  "timer_dump": {
    "description": "Dumps debug timing info"
  },
  "ct": {
    "description": "Puts timer info in clipboard"
  },
  "dump_checksum": {
    "description": "Compute and store the checksum in a file"
  },
  "compare_to_last_checksum": {
    "description": "Compare current checksum with the most recent dump"
  },
  "dump_synchronized_members": {
    "description": "Dump the synchronized game state (the one that has checksum ID 2)"
  },
  "add_legitimacy": {
    "arguments": [
      "<TAG>",
      "<value>"
    ],
    "description": "Adds legitimacy to specified tag. add_legitimacy TAG amount"
  },
  "dbg_tf_fulfillment": {
    "description": "Show the managed fulfillment of a taskforce (exepected number of ships after all ships have been merged in)"
  },
  "damage_units": {
    "arguments": [
      "<org>",
      "<str>",
      "<num>"
    ],
    "description": "Damage or heal selected units or units under pointer if there is none selected. Enter 1 argument to apply damage for both types, two for individual both types"
  },
  "add_critical_hit": {
    "arguments": [
      "<critical_hit_name>"
    ],
    "description": "add critical hit to selected ships"
  },
  "clear_critical_hits": {
    "description": "clear all critical hits"
  },
  "add_exile_manpower": {
    "arguments": [
      "<TAG>",
      "<value>"
    ],
    "description": "Adds legitimacy to specified tag. add_legitimacy TAG amount"
  },
  "bypass_invasion_superiority_check": {
    "aliases": [
      "bisc"
    ],
    "description": "Ignore superiority in the strategic areas crossed by a naval invasion order"
  },
  "add_fleet_arrow": {
    "available_in_release_build": false,
    "arguments": [
      "color"
    ],
    "description": "Add an arrow around a strategic region"
  },
  "toggle_offset_ai_daily_update": {
    "available_in_release_build": false,
    "description": "Whether a country's ai daily update should be spread over a day"
  },
  "get_capital": {
    "arguments": [
      "<Country tag>"
    ],
    "description": "Get the capital of a country"
  },
  "dbg_task_force_role_insignia_assignment": {
    "aliases": [
      "tfria"
    ],
    "description": "print the role that would be deduced for the selected task force"
  },
  "imgui": {
    "description": "Controls ImGui UIs. See the sub commands.",
    "argument_completion_support": true
  },
  "grow_intel_network": {
    "description": "Grow the intel network in the specified tag"
  },
  "print_intel_network": {
    "description": "Print intel network related information"
  },
  "print_intel_values": {
    "description": "Print the intel a country has over another"
  },
  "clear_intel_pools": {
    "description": "Reset the specified intel pool"
  },
  "print_radar_intel": {
    "description": "Print the intel value breakdown generated by radar"
  },
  "add_intel": {
    "description": "Set the values of a static intel pool against a specific country. E.g. `add_intel GER POL army=10`"
  },
  "force_operative_detection": {
    "aliases": [
      "snitch"
    ],
    "description": "Print intel network related information"
  },
  "prevent_operative_detection": {
    "description": "Prevent a country from detecting and harming foreign operatives"
  },
  "emulate_ai_operative_assignment": {
    "description": "Log ai operative assignment if it were to run this tick. Takes as first argument the tag of the country to test, default to the player's."
  },
  "select": {
    "available_in_release_build": false,
    "arguments": [
      "<object id>",
      "<object type id> (optional)"
    ],
    "aliases": [
      "sel"
    ],
    "description": "select object by id"
  },
  "railwaygun": {
    "available_in_release_build": false,
    "aliases": [
      "rg"
    ],
    "description": "create railway gun in supply capital"
  },
  "railwaygun_damage": {
    "available_in_release_build": false,
    "aliases": [
      "rg_damage"
    ],
    "description": "damage railway guns"
  },
  "loc_check_focuses": {
    "description": "Check national focuses for missing localization"
  },
  "loc_check_events": {
    "description": "Check events for missing localization"
  },
  "loc_check_modifiers": {
    "description": "Check modifiers for missing localization"
  },
  "loc_check_decisions": {
    "description": "Check decisions for missing localization"
  },
  "loc_check_national_spirits": {
    "description": "Check national spirits for missing localization"
  },
  "loc_check_characters": {
    "description": "Check characters for missing localization"
  },
  "loc_check": {
    "description": "Check for missing localization"
  },
  "set_weather": {
    "arguments": [
      "<weather_type>"
    ],
    "description": "Sets the weather for the selected province (and corresponding region)"
  },
  "set_mud": {
    "description": "Sets mud for the selected province"
  },
  "add_rain": {
    "arguments": [
      "<rain_amount>"
    ],
    "description": "Adds rain to the selected province"
  },
  "add_snow": {
    "arguments": [
      "<snow_amount>"
    ],
    "description": "Adds snow to the selected province"
  },
  "dump_equipment_loc": {
    "arguments": [
      "desc: Dump equipment descriptions instead of the names",
      "<country_tag>: Multiple allowed. Only include loc strings for the given countries. Generic loc strings are included if no tags are given, or with argument 'generic'.",
      "<type>: Multiple allowed. Only include equipment that are all of the given types, e.g. 'armor anti_tank' will only include tank destroyers.",
      "path=<filepath>: File path to write the dump to. Default is 'logs/equipment_loc.csv'."
    ],
    "description": "Dumps equipment loc strings to file. All arguments are optional."
  },
  "print_controllers": {
    "description": "Prints countries controlled by human players."
  },
  "bop_show": {
    "description": "Shows current country's active power balances."
  },
  "bop_set": {
    "arguments": [
      "<ID>"
    ],
    "description": "Activates a power balance for the current country."
  },
  "bop_remove": {
    "arguments": [
      "<ID>"
    ],
    "description": "Deactivates a power balance for the current country."
  },
  "bop_add": {
    "arguments": [
      "<ID>",
      "<value>"
    ],
    "description": "Changes the value of the specified power balance."
  },
  "bop_addmod": {
    "arguments": [
      "<ID>",
      "<ModID>"
    ],
    "description": "Adds static modifier to a power balance."
  },
  "bop_rmmod": {
    "arguments": [
      "<ID>",
      "<ModID>"
    ],
    "description": "Removes static modifier from a power balance."
  },
  "easy_decisions": {
    "aliases": [
      "ezd"
    ],
    "description": "Toggles Easy Decisions Mode which makes all decisions with days_remove take only 1 day to be removed, and all decisions with cost not have any cost or cost trigger."
  },
  "log_advisor_trait_errors": {
    "description": "Logs all instances of unit leader advisors not having the corresponding unit leader traits."
  },
  "deleteallairwings": {
    "aliases": [
      "delallair"
    ],
    "description": "Delete all airwings."
  },
  "ListIncorrectCenterOfRegions": {
    "available_in_release_build": false,
    "description": "List regions center point that is located within another region"
  },
  "endraids": {
    "available_in_release_build": false,
    "arguments": [
      " <Success Level: 1-4 OR { failure, limitedsuccess, success, criticalsuccess}>"
    ],
    "description": "Instantly end all active raids, optionally with a specific success level"
  },
  "prepareraids": {
    "available_in_release_build": false,
    "arguments": [
      " <[Optional] the degree to which the raid should be prepared (0.0-1.0)>"
    ],
    "description": "Instantly complete preparation of all active raids, optionally to a specific progress level"
  },
  "restart": {
    "available_in_release_build": false,
    "description": "Restart the game as the current country"
  },
  "freefocuses": {
    "aliases": [
      "ff"
    ],
    "description": "Enable freely activating any focuses"
  },
  "province_ids": {
    "aliases": [
      "pid"
    ],
    "description": "Show province IDs on the map"
  },
  "energy_ratio": {
    "arguments": [
      "Energy ratio"
    ],
    "aliases": [
      "er"
    ],
    "description": "Set Energy Ratio for the factories without coal consumption"
  },
  "auto_unpause": {
    "available_in_release_build": false,
    "arguments": [
      "[speed 1-5]"
    ],
    "description": "Auto-unpause at given speed (1-5) when clients catch up. No argument to disable."
  },
  "InternationalMarket.RequestPurchase": {
    "arguments": [
      "<SellerTag>",
      "<BuyerTag>",
      "<PaidCivs>",
      "<EquipmentName>",
      "<EquipmentAmount>"
    ],
    "description": "Request Equipment Purchase."
  },
  "InternationalMarket.CancelPurchase": {
    "arguments": [
      "<SellerTag>",
      "<BuyerTag>",
      "<ContractIndex>"
    ],
    "description": "Cancel the purchase contract between the seller and the buyer"
  },
  "InternationalMarket.ReserveToMarketStockpile": {
    "arguments": [
      "<EquipmentName>",
      "<EquipmentAmount>"
    ],
    "description": "Reserve equipment from main stockpile to market stockpile"
  },
  "InternationalMarket.ReleaseFromMarketStockpile": {
    "arguments": [
      "<EquipmentName>",
      "<EquipmentAmount>"
    ],
    "description": "Release equipment to main stockpile from market stockpile"
  },
  "add_cic_bank": {
    "arguments": [
      "<value>"
    ],
    "aliases": [
      "stonks",
      "cic",
      "bank"
    ],
    "description": "Add CIC to the CIC bank (negative value subtracts)"
  },
  "InternationalMarket.SetPriceLevel": {
    "arguments": [
      "<EquipmentName>",
      "<Level>"
    ],
    "description": "Sets the price level for the given equipment in the Market Stockpile"
  },
  "InternationalMarket.AddSubsidyForTags": {
    "arguments": [
      "<CIC>",
      "<Archetype>",
      "<Tag>"
    ],
    "description": "Add a Equipment Subsidy to the player's international market."
  },
  "InternationalMarket.AddSubsidyForTrigger": {
    "arguments": [
      "<CIC>",
      "<Archetype>",
      "<ScriptedTrigger> "
    ],
    "description": "Add a Equipment Subsidy to the player's international market."
  },
  "InternationalMarket.Dev.SetMarketRequestAutomation": {
    "arguments": [
      "<AcceptMarketAccess>",
      "<SendMarketAccess>",
      "<AcceptPurchase>"
    ],
    "description": "Set the market requests automation state"
  },
  "AddFunds": {
    "arguments": [
      "<Industrial Organisation token> (optional)",
      "<Funds amount> (optional)"
    ],
    "aliases": [
      "mio.AddFunds",
      "IndustrialOrganisation.AddFunds"
    ],
    "description": "\"Add funds to one or all Military Industrial Organisations\nex:\nAddFunds org_token 2000\nAddFunds org_token // default added funds is NDefines::NIndustrialOrganisation::FUNDS_FOR_SIZE_UP\nAddFunds 2000 // Funds added to all the player's MIOs\nAddFunds // default funds amount added to all the player's MIOs\"",
    "argument_completion_support": true
  },
  "AddTaskCapacity": {
    "arguments": [
      "<Industrial Organisation token> (optional)",
      "<capacity amount> (optional)"
    ],
    "aliases": [
      "mio.AddTaskCapacity",
      "IndustrialOrganisation.AddTaskCapacity"
    ],
    "description": "\"Add task capacity to one or all Military Industrial Organisations.\nValue can be negative but final task capacity will be capped at 0.\nex:\nAddTaskCapacity org_token 2\nAddTaskCapacity org_token // adds 1 capacity\nAddTaskCapacity 2 // adds input capacity to all the player's MIOs\nAddTaskCapacity // adds 1 capacity to all the player's MIOs\"",
    "argument_completion_support": true
  },
  "AddSize": {
    "arguments": [
      "<Industrial Organisation token> (optional)",
      "<capacity amount> (optional)"
    ],
    "aliases": [
      "mio.AddSize",
      "IndustrialOrganisation.AddSize"
    ],
    "description": "\"Add sizes to one or all Military Industrial Organisations.\nex:\nAddSize org_token 2\nAddSize org_token // adds 1 size\nAddSize 2 // adds input size to all the player's MIOs\nAddSize // adds 1 size to all the player's MIOs\"",
    "argument_completion_support": true
  },
  "sp_fast": {
    "description": "\"All phases in Special Projects take now 1 day to complete.\nFor prototype phase, it's the iterations that will take 1 day. And it will require as many iterations as usual.\nex:\nsp_fast\""
  },
  "sp_instant": {
    "description": "\"All started Special Projects finish on the daily tick. It skips the iterations of the Prototyping phase and their reward.\nex:\nsp_instant\""
  },
  "sp_available": {
    "description": "\"Trigger available returns true for all Special Projects.\nex:\nsp_available\""
  },
  "sp_unlock_all": {
    "description": "\"All Special Projects are always visible and available. Whether or not the triggers returns true, and whether the parents are completed.\nex:\nsp_unlock_all\""
  },
  "sp_add_scientist": {
    "arguments": [
      "<Level> (optional)",
      "<Specialization> (optional)"
    ],
    "description": "\"Add a scientist. Is specified a specialization and level that will be applied to the scientist. If no specialization is specified the level will be applied to all.\nex:\nsp_add_scientist 3 nuclear\nsp_add_scientist 2\nsp_add_scientist\""
  },
  "sp_add_mastermind": {
    "description": "\"Add a scientist with max skill in all specializations\""
  },
  "sp_add_selected_scientist_level": {
    "arguments": [
      "<Level>",
      "<Specialization> (optional)"
    ],
    "description": "\"Add level and if specified, specifically to a specialization for a scientist. If no specialization is specified, the level will be added for each specialization. Requires the facility view with an attached scientist to be open.\nex:\nsp_add_scientist_level 3 nuclear\nsp_add_scientist_level 2\""
  },
  "sp_set_selected_scientist_level": {
    "arguments": [
      "<Level>",
      "<Specialization> (optional)"
    ],
    "description": "\"Set level and if specified, specifically to a specialization for a scientist. If no specialization is specified, the level will be added for each specialization. Requires the facility view with an attached scientist to be open.\nex:\nsp_set_scientist_level 3 nuclear\nsp_set_scientist_level 2\""
  },
  "sp_add_selected_scientist_trait": {
    "arguments": [
      "<Trait>"
    ],
    "description": "\"Add a trait to the scientist. Requires the facility view with an attached scientist to be open.\nex:\nsp_add_scientist_trait my_trait_token\""
  },
  "sp_remove_selected_scientist_trait": {
    "description": "\"Remove a trait from the scientist. Requires the facility view with an attached scientist to be open.\nex:\nsp_remove_selected_scientist_trait my_trait_token\""
  },
  "sp_research_all": {
    "aliases": [
      "sp_ra"
    ],
    "description": "\"Research all special projects. If no scientist exist it will create one, otherwise it will pick an arbitrary one. Imagine there is a secret hidden facility\nin a controlled province where the projects are researched.\""
  },
  "sp_breakthrough": {
    "arguments": [
      "<amount> optional <specialization>"
    ],
    "aliases": [
      "sp_br"
    ],
    "description": "\"Create breakthrough points.\""
  },
  "toggle_hidden_techs": {
    "arguments": [],
    "aliases": [
      "tht"
    ],
    "description": "\"Toggle show/hide all hidden techs.\""
  },
  "sp_prototype_reward": {
    "arguments": [],
    "aliases": [
      "spr"
    ],
    "description": "\"Trigger a specified prototype reward during a project.\"",
    "argument_completion_support": true
  },
  "mastery": {
    "arguments": [
      "mastery amount",
      "[optional] track name"
    ],
    "description": "Give doctrine mastery, globally or to a specific track"
  },
  "collaboration": {
    "description": "Adds collaborations against selected country. Right click to select a country and use \"collaboration 0.3\""
  },
  "add_fake_armies": {
    "description": "Creates fake intel armies for the player"
  },
  "retire_country_leader": {},
  "clear_tech": {},
  "add_tech": {},
  "spawn_3D_models": {},
  "add_subsidies": {},
  "add_subsidies_second": {}
}

### tweakables

{
  "Operation.Instant": {
    "type": "bool"
  },
  "IntelNetwork.Instant": {
    "type": "bool"
  },
  "Debug.OldCombat": {
    "type": "bool"
  },
  "Focus.NoChecks": {
    "type": "bool"
  },
  "Focus.AutoComplete": {
    "type": "bool"
  },
  "fa": {
    "type": "bool"
  },
  "Focus.IgnorePrerequisites": {
    "type": "bool"
  },
  "BattleSound.PlayBackground": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "BattleSound.Debug": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Objects": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Transparent": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Shadows": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.ShadowBlur": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "PostEffectVolumes.Draw": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "ShowBorderTypes": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Postfx": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Tree": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Terrain": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Rivers": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Water": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Borders": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Draw.Refractions": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Tree.MipLevels": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Terrain.MipLevels": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "BorderLOD.Threaded": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "PostEffectVolumes.Enabled": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "CounterIntelligence.TestShieldColors": {
    "type": "bool"
  },
  "supply_debug.show_debug_lines_rail": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "supply_debug.show_debug_lines_train": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "supply_debug.show_debug_lines_supply": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "supply_debug.show_debug_rivers": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "ShowTechBonus": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Debug.DeleteUnitEachTick": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Decision.NoChecks": {
    "type": "bool"
  },
  "Decision.FastRemove": {
    "type": "bool"
  },
  "resistance_system": {
    "type": "bool"
  },
  "Agency.AutoComplete": {
    "type": "bool"
  },
  "Agency.KeepExcessOperatives": {
    "type": "bool"
  },
  "Agency.InstantSlotUnlock": {
    "type": "bool"
  },
  "ApplicationUtils.Update": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.DebugMin": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.DebugMax": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.Debug.LevelsSampleRate": {
    "available_in_release_build": false,
    "type": "integer"
  },
  "Audio.Debug.Levels": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "guibounds": {
    "type": "bool"
  },
  "Update.Particles": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Update.Animations": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Normals": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "BoundingVolumes": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Collisions": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Mesh.Names": {
    "type": "bool"
  },
  "Mesh.TextureNames": {
    "type": "bool"
  },
  "GUI.Wireframe": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Mesh.Wireframe": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Mesh.MipLevels": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Particle.Wireframe": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Particle.UseRingbuffer": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Particle.MipLevels": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.Debug": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.Debug.ExtendedRange": {
    "available_in_release_build": false,
    "type": "bool"
  },
  "Audio.Compressor": {
    "available_in_release_build": false,
    "type": "bool"
  }
}

