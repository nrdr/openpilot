 JSON Configuration Guide for ConfigDrivenPanel body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; background-color: #f9f9f9; color: #333; } h1, h2, h3, h4 { color: #2c3e50; } table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #fff; } table, th, td { border: 1px solid #bdc3c7; } th, td { padding: 10px; text-align: left; } th { background-color: #ecf0f1; } pre { background-color: #ecf0f1; padding: 10px; overflow-x: auto; } code { font-family: Consolas, monospace; background-color: #ecf0f1; padding: 2px 4px; border-radius: 4px; } blockquote { border-left: 4px solid #bdc3c7; padding-left: 16px; color: #7f8c8d; margin: 20px 0; } ul, ol { margin-left: 20px; }

# JSON Configuration Guide for ConfigDrivenPanel

This document provides a comprehensive overview of the JSON configuration format used to define panels, groups, and controls within the `ConfigDrivenPanel` system. Whether you're customizing vehicle settings, adding utility commands, or managing parameters, this guide will help you understand and utilize the available options effectively.

## Table of Contents

- [JSON Configuration Guide for ConfigDrivenPanel](#json-configuration-guide-for-configdrivenpanel)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Overall JSON Structure](#overall-json-structure)
    - [Top-Level Properties](#top-level-properties)
    - [Groups](#groups)
  - [Group Object](#group-object)
    - [Properties](#properties)
  - [Control Object](#control-object)
    - [Common Properties](#common-properties)
    - [Control Types](#control-types)
      - [Toggle Control](#toggle-control)
        - [Properties:](#properties-1)
      - [Float Control](#float-control)
        - [Properties:](#properties-2)
      - [Integer Control](#integer-control)
        - [Properties:](#properties-3)
      - [Selection Control](#selection-control)
        - [Properties:](#properties-4)
      - [Static Param Display Control](#static-param-display-control)
        - [Properties:](#properties-5)
      - [Segmented Control](#segmented-control)
        - [Properties:](#properties-6)
      - [Param Viewer Control](#param-viewer-control)
        - [Properties:](#properties-7)
      - [Param List Viewer Control](#param-list-viewer-control)
        - [Properties:](#properties-8)
      - [File Viewer Control](#file-viewer-control)
        - [Properties:](#properties-9)
      - [Recent Changes Control](#recent-changes-control)
        - [Properties:](#properties-10)
      - [Command Button Control](#command-button-control)
        - [Properties:](#properties-11)
    - [Custom Controls](#custom-controls)
  - [Conditions](#conditions)
    - [Condition Property Types](#condition-property-types)
    - [Condition Types](#condition-types)
    - [Composite Conditions](#composite-conditions)
  - [Examples](#examples)
    - [Full Configuration Example](#full-configuration-example)
    - [Individual Control Examples](#individual-control-examples)
      - [Toggle Control with Conditions](#toggle-control-with-conditions)
      - [Float Control with Default Value](#float-control-with-default-value)
      - [Command Button Control with Confirmation](#command-button-control-with-confirmation)
      - [Segmented Control Example](#segmented-control-example)
      - [Conditional Visibility Based on Parameter Values](#conditional-visibility-based-on-parameter-values)
      - [Advanced Condition Example](#advanced-condition-example)
  - [Optional vs. Required Properties](#optional-vs-required-properties)
    - [Required Properties](#required-properties)
    - [Optional Properties](#optional-properties)
  - [Notes and Best Practices](#notes-and-best-practices)
  - [Conclusion](#conclusion)

- - -

## Introduction

The `ConfigDrivenPanel` system leverages JSON files to dynamically generate user interface panels, organizing settings into groups and controls. This approach allows for flexible and scalable configuration management, enabling developers and advanced users to customize functionalities without altering the underlying codebase.

## Overall JSON Structure

A configuration JSON file defines the entire panel's structure, including its name, icon, description, and the groups and controls it contains.

### Top-Level Properties

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `menuName` | String | The name of the panel displayed in the UI. | Yes | \-  |
| `menuIcon` | String | The icon associated with the panel. | Yes | \-  |
| `menuDescription` | String | A brief description of the panel. | Yes | \-  |
| `persistentParams` | Array | List of parameter names that persist across sessions. | No  | `[]` |
| `clearOnManagerStartParams` | Array | Parameters to clear when the manager starts. | No  | `[]` |
| `clearOnOnroadTransitionParams` | Array | Parameters to clear during on-road transitions. | No  | `[]` |
| `clearOnOffroadTransitionParams` | Array | Parameters to clear during off-road transitions. | No  | `[]` |
| `groups` | Array | An array of group objects defining UI sections and controls. | Yes | \-  |

### Groups

The `groups` array contains objects that define distinct sections within the panel, each housing related controls.

## Group Object

Each group organizes related controls under a common title and can optionally include a reset button.

### Properties

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `groupName` | String | A unique identifier for the group. | Yes | \-  |
| `title` | String | The display title of the group in the UI. | Yes | \-  |
| `enableResetButton` | Boolean | Determines if a reset button is available for the group. | No  | `false` |
| `controls` | Array | An array of control objects within the group. | Yes | \-  |
| `type` | String | The type of group, e.g., `"tabPanel"`. | No  | `"group"` |

> **Example:**
>
> ```
> {
>   "groupName": "systemPreferencesGroup",
>   "title": "System Preferences: (Tap item for desc)",
>   "enableResetButton": false,
>   "controls": [
>     // Control objects here
>   ]
> }
>
> ```

## Control Object

Controls are interactive elements within a group that allow users to view or modify settings. Each control type has specific properties.

### Common Properties

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | The type of control (e.g., toggle, float, selection). | Yes | \-  |
| `param` | String | The parameter name associated with the control. | Yes | \-  |
| `title` | String | The display title of the control. | Yes | \-  |
| `desc` | String | A description or tooltip for the control. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |
| `conditions` | Object | **[LEGACY]** Defines conditions for both visibility and enabled state. Use `visibleConditions` and `enableConditions` instead for granular control. | No  | \-  |
| `visibleConditions` | Object | Defines conditions that control whether the control is visible or hidden. | No  | \-  |
| `enableConditions` | Object | Defines conditions that control whether the control is enabled or disabled (grayed out). | No  | \-  |

### Control Types

#### Toggle Control

A switch that allows users to enable or disable a specific feature.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"toggle"`. | Yes | \-  |
| `param` | String | The parameter name to toggle. | Yes | \-  |
| `title` | String | The display title of the toggle. | Yes | \-  |
| `desc` | String | Description of what the toggle controls. | Yes | \-  |
| `disable` | Boolean | Disables the toggle if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the toggle if set to `true`. | No  | `false` |
| `conditions` | Object | Conditions to determine the toggle's availability. | No  | \-  |

**Example:**

```
{
  "type": "toggle",
  "param": "FordPrefEnableDebugLogs",
  "title": "Enable Debug Logging",
  "desc": "Enables additional debug output.",
  "disable": false,
  "hidden": false,
  "conditions": {
    "git_remote": ["ford-op/sp-dev-c3"],
    "git_branch": []
  }
}
```

#### Float Control

Allows users to adjust a floating-point parameter within a specified range.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"float"`. | Yes | \-  |
| `param` | String | The parameter name to adjust. | Yes | \-  |
| `title` | String | The display title of the float control. | Yes | \-  |
| `desc` | String | Description of what the float control adjusts. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `min` | Number | The minimum allowable value. | Yes | \-  |
| `max` | Number | The maximum allowable value. | Yes | \-  |
| `increment` | Number | The step increment for adjusting the value. | Yes | \-  |
| `division` | Number | Division factor for displaying the value. | Yes | `1.0` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |
| `conditions` | Object | Conditions to determine the control's availability. | No  | \-  |

**Example:**

```
{
  "type": "float",
  "param": "FordLatTuningLaneChgModifier",
  "title": "Lane Change Modifier",
  "desc": "Adjust lane change curvature aggressiveness (lower = slower).",
  "disable": false,
  "hidden": false,
  "min": 0.0,
  "max": 1.0,
  "increment": 0.05,
  "division": 100.0,
  "conditions": {
    "git_remote": ["any"],
    "git_branch": []
  }
}
```

#### Integer Control

Allows users to adjust an integer parameter within a specified range.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"integer"`. | Yes | \-  |
| `param` | String | The parameter name to adjust. | Yes | \-  |
| `title` | String | The display title of the integer control. | Yes | \-  |
| `desc` | String | Description of what the integer control adjusts. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `min` | Number | The minimum allowable value. | Yes | \-  |
| `max` | Number | The maximum allowable value. | Yes | \-  |
| `increment` | Number | The step increment for adjusting the value. | Yes | \-  |
| `unit` | String | The unit suffix to display (e.g., "mph", "%", "km/h"). | No  | `""` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |
| `conditions` | Object | Conditions to determine the control's availability. | No  | \-  |

**Example:**

```
{
  "type": "integer",
  "param": "SpeedLimitValueOffset",
  "title": "Fixed Offset Value",
  "desc": "Fixed speed offset value in mph/km/h",
  "min": -30,
  "max": 30,
  "increment": 1,
  "unit": "mph",
  "conditions": {
    "allConditionsTrue": [
      { "paramValueEquals": { "SpeedLimitOffsetType": "1" } }
    ]
  }
}
```

#### Selection Control

Provides a dropdown or selection interface for choosing among predefined options.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"selection"`. | Yes | \-  |
| `param` | String | The parameter name to set based on selection. | Yes | \-  |
| `title` | String | The display title of the selection control. | Yes | \-  |
| `desc` | String | Description of what the selection controls. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |
| `options` | Array | An array of option objects defining selectable items. | Yes | \-  |
| `conditions` | Object | Conditions to determine the control's availability. | No  | \-  |

**Option Object Properties:**

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `name` | String | The display name of the option. | Yes | \-  |
| `value` | String | The value to set when the option is selected. | Yes | \-  |

**Example:**

```
{
  "type": "selection",
  "param": "FordSelectedVehicleModel",
  "title": "Vehicle Model",
  "desc": "Select your vehicle model",
  "disable": false,
  "hidden": false,
  "options": [
    { "name": "F-150 14th Gen (21-23)", "value": "FORD_F_150_MK14" },
    { "name": "F-150 Lightning 1st Gen", "value": "FORD_F_150_LIGHTNING_MK1" },
    { "name": "Mustang Mach-E 1st Gen", "value": "FORD_MUSTANG_MACH_E_MK1" }
  ]
}
```

#### Static Param Display Control

Displays a parameter value as read-only text in the UI.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"static_param_display"`. | Yes | \-  |
| `param` | String | The parameter name to display. | Yes | \-  |
| `title` | String | The display title of the control. | Yes | \-  |
| `desc` | String | Description of what the parameter represents. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No | `false` |
| `conditions` | Object | Conditions to determine the control's availability. | No | \-  |

**Example:**

```
{
  "type": "static_param_display",
  "param": "DongleId",
  "title": "Device ID",
  "desc": "Unique identifier for this device",
  "disable": false,
  "hidden": false,
  "conditions": {
    "git_remote": ["any"],
    "git_branch": []
  }
}
```

#### Segmented Control

Provides a segmented button interface for selecting one option among multiple predefined options.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"segmented_control"`. | Yes | \-  |
| `param` | String | The parameter name to set based on selection. | Yes | \-  |
| `title` | String | The display title of the segmented control. | Yes | \-  |
| `desc` | String | Description of what the segmented control does. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |
| `options` | Array | An array of option objects defining selectable segments. | Yes | \-  |
| `defaultValue` | String | The default value to select if not set. | No  | \-  |
| `conditions` | Object | Conditions to determine the control's availability. | No  | \-  |

**Option Object Properties:**

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `name` | String | The display name of the segment. | Yes | \-  |
| `value` | String | The value to set when the segment is selected. | Yes | \-  |

**Example:**

```
{
  "type": "segmented_control",
  "param": "FordLatTuningTuningProfile",
  "title": "Tuning Profile",
  "desc": "Sets the tuning aggressiveness",
  "disable": false,
  "hidden": false,
  "options": [
    { "name": "Low", "value": "1" },
    { "name": "Medium", "value": "2" },
    { "name": "High", "value": "3" },
    { "name": "Custom", "value": "4" }
  ],
  "defaultValue": "2",
  "conditions": {
    "allConditionsTrue": [
      { "git_remote": ["any"] },
      { "git_branch": [] }
    ]
  }
}
```

#### Param Viewer Control

Displays the current value of a specified parameter in a read-only format.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"param_viewer"`. | Yes | \-  |
| `param` | String | The parameter name to view. | Yes | \-  |
| `title` | String | The display title of the parameter viewer. | Yes | \-  |
| `desc` | String | Description of what the viewer displays. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |

**Example:**

```
{
  "type": "param_viewer",
  "param": "LiveParameters",
  "title": "Live Parameters",
  "desc": "View live parameters",
  "disable": false,
  "hidden": false
}
```

#### Param List Viewer Control

Provides a comprehensive view of all available parameters, allowing users to browse through them.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"param_list_viewer"`. | Yes | \-  |
| `param` | String | The parameter name to view all parameters. | Yes | \-  |
| `title` | String | The display title of the parameter list viewer. | Yes | \-  |
| `desc` | String | Description of what the viewer displays. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |

**Example:**

```
{
  "type": "param_list_viewer",
  "param": "AllParameters",
  "title": "All Parameters",
  "desc": "View all available parameters",
  "disable": false,
  "hidden": false
}
```

#### File Viewer Control

Allows users to view the contents of a specified file within the application.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"file_viewer"`. | Yes | \-  |
| `path` | String | Relative path to the file to be viewed. | Yes | \-  |
| `title` | String | The display title of the file viewer. | Yes | \-  |
| `desc` | String | Description of what the file viewer does. | Yes | \-  |
| `header` | String | Optional header text for the dialog displaying the file. | No  | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |

**Example:**

```
{
  "type": "file_viewer",
  "path": "CHANGELOGS_BP.md",
  "title": "BluePilot Changelog",
  "desc": "View the BluePilot changelog",
  "header": "BluePilot Changelog",
  "disable": false,
  "hidden": false
}
```

#### Recent Changes Control

Allows users to view recent changes and updates for the current version using the BPRecentChangesDialog.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"recent_changes"`. | Yes | \-  |
| `title` | String | The display title of the recent changes viewer. | Yes | \-  |
| `desc` | String | Description of what the recent changes viewer does. | Yes | \-  |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |

**Example:**

```
{
  "type": "recent_changes",
  "title": "Recent Changes",
  "desc": "View recent changes and updates for the current version",
  "disable": false,
  "hidden": false
}
```

#### Command Button Control

Executes a specified command when clicked, optionally requiring user confirmation.

##### Properties:

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `type` | String | Must be `"command_button"`. | Yes | \-  |
| `command` | String | The command to execute. | Yes | \-  |
| `working_dir` | String | The working directory to execute the command in. | No  | Current directory |
| `command_timeout_ms` | Integer | Timeout in milliseconds for the command execution. | No  | `120000` (2 minutes) |
| `title` | String | The display title of the command button. | Yes | \-  |
| `desc` | String | Description of what the command does. | Yes | \-  |
| `button_text` | String | The text displayed on the button. | No  | `"EXECUTE"` |
| `confirm` | Boolean | Whether to prompt for confirmation before executing the command. | No  | `false` |
| `confirm_text` | String | The confirmation message displayed to the user. Supports HTML. | No  | Default confirmation message |
| `confirm_button_text` | String | The text for the main confirmation button. | No  | `"Yes"` |
| `cancel_button_text` | String | The text for the cancel button. | No  | `"Cancel"` |
| `showRetry` | Boolean | Whether to show the retry button when the command fails. | No  | `true` |
| `actionButtons` | Array | Array of action button objects to display after command execution. See Action Buttons below. | No  | `[]` |
| `disable` | Boolean | Disables the control if set to `true`. | No  | `false` |
| `hidden` | Boolean | Hides the control if set to `true`. | No  | `false` |

##### Action Buttons

Action buttons are optional buttons that appear in the command execution dialog after the command completes. They can be configured to show based on whether the command succeeded or failed.

**Action Button Properties:**

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `text` | String | The text displayed on the action button. | Yes | \-  |
| `action` | String | Built-in action to perform. Currently supports: `"reboot"`. Mutually exclusive with `command`. | No  | \-  |
| `command` | String | Shell command to execute when clicked. Mutually exclusive with `action`. | No  | \-  |
| `showWhen` | String | When to display this button: `"success"` (only on successful command completion), `"failure"` (only on command failure), or `"always"` (show regardless of outcome). | No  | `"always"` |
| `confirm` | Boolean | Whether to prompt for confirmation before executing the action. | No  | `false` |
| `confirm_text` | String | The confirmation message. Supports HTML. | No  | `"Are you sure?"` |
| `confirm_yes_text` | String | Text for the confirmation button. | No  | `"Yes"` |
| `confirm_no_text` | String | Text for the cancel button. | No  | `"No"` |

**Example:**

```json
{
  "type": "command_button",
  "command": "/data/openpilot/scripts/force_branch_update.sh bp-5.0-beta",
  "working_dir": "/data/openpilot",
  "command_timeout_ms": 900000,
  "title": "Force Update to bp-5.0-beta",
  "desc": "Clones a fresh copy of bp-5.0-beta and replaces /data/openpilot. Uses automatic rollback on failure.",
  "button_text": "Force Update",
  "confirm": true,
  "confirm_text": "This will force update to bp-5.0-beta. Continue?",
  "confirm_button_text": "Yes, Force Update",
  "cancel_button_text": "Cancel",
  "showRetry": true,
  "actionButtons": [
    {
      "text": "Reboot Device",
      "action": "reboot",
      "showWhen": "success",
      "confirm": true,
      "confirm_text": "The update is complete. Reboot now to apply changes?",
      "confirm_yes_text": "Reboot Now",
      "confirm_no_text": "Later"
    },
    {
      "text": "View Error Logs",
      "command": "tail -n 100 /data/community/crashes/*",
      "showWhen": "failure",
      "confirm": false
    }
  ],
  "disable": false,
  "hidden": false
}
```

### Custom Controls

The `ConfigDrivenPanel` system also supports custom control types beyond the standard ones listed above. These controls can be defined and integrated based on specific requirements.

**Example:**

```
{
  "type": "custom_control",
  "param": "CustomParam",
  "title": "Custom Control",
  "desc": "Description for custom control.",
  "disable": false,
  "hidden": false,
  "customProperty1": "Value1",
  "customProperty2": 10,
  "conditions": {
    "paramValueEquals": { "CustomParam": "Enabled" }
  }
}
```

_Note: Custom controls require corresponding implementation in the codebase to handle their unique properties and behaviors._

## Conditions

Conditions determine the visibility and behavior of controls based on specific criteria. They enable dynamic and context-sensitive UI elements.

### Condition Property Types

There are three ways to apply conditions to controls:

1. **`conditions`** (Legacy) - Controls BOTH visibility and enabled state
   - When conditions fail, the control is both hidden AND disabled
   - Maintained for backward compatibility
   - **Recommendation:** Use `visibleConditions` and `enableConditions` instead for better control

2. **`visibleConditions`** (Recommended) - Controls visibility only
   - When conditions are met: control is shown
   - When conditions fail: control is completely hidden from the UI
   - Use this when you want to show/hide controls based on parameter values or system state

3. **`enableConditions`** (Recommended) - Controls enabled state only
   - When conditions are met: control is enabled (interactive)
   - When conditions fail: control is visible but disabled (grayed out)
   - Use this when you want to show a control but prevent interaction based on conditions

**Example use cases:**

```json
{
  "type": "integer",
  "param": "SpeedLimitValueOffset",
  "title": "Fixed Offset Value",
  "visibleConditions": {
    "paramValueEquals": { "SpeedLimitOffsetType": "1" }
  }
}
```
In this example, the control only appears when the offset type is set to "Fixed" (value "1").

```json
{
  "type": "toggle",
  "param": "ExperimentalMode",
  "title": "Experimental Mode",
  "enableConditions": {
    "allConditionsTrue": [
      { "isOnroad": true },
      { "hasLongitudinalControl": true }
    ]
  }
}
```
In this example, the toggle is always visible, but only enabled when the vehicle is onroad and has longitudinal control.

### Condition Types

*   **`paramValueEquals`:** Checks if a parameter equals a specified value.

    ```
    "paramValueEquals": {
      "ParameterName": "ExpectedValue"
    }

    ```

*   **`paramValueGreaterThan`:** Checks if a parameter's value is greater than a specified number.

    ```
    "paramValueGreaterThan": {
      "ParameterName": 70
    }

    ```

*   **`paramValueLessThan`:** Checks if a parameter's value is less than a specified number.

    ```
    "paramValueLessThan": {
      "ParameterName": 90
    }

    ```

*   **`paramValueInRange`:** Checks if a parameter's value falls within a specified range.

    ```
    "paramValueInRange": {
      "ParameterName": {
        "min": 10,
        "max": 20
      }
    }

    ```

*   **`git_remote`:** Validates against specified Git remote repositories.

    ```
    "git_remote": ["remote1", "remote2"]

    ```

*   **`git_branch`:** Validates against specified Git branches.

    ```
    "git_branch": ["branch1", "branch2"]

    ```

*   **`paramIsTrue`:** Checks if a boolean parameter is true. (Preferred over `onlyWhenTheseParams`)

    ```
    "paramIsTrue": "OnroadScreenOffControl"

    ```

    Multiple params (all must be true):

    ```
    "paramIsTrue": ["EnableMads", "LongitudinalEnable"]

    ```

*   **`paramIsFalse`:** Checks if a boolean parameter is false.

    ```
    "paramIsFalse": "DisableLogging"

    ```

    Multiple params (all must be false):

    ```
    "paramIsFalse": ["Feature1", "Feature2"]

    ```

*   **`onlyWhenTheseParams`:** Ensures that certain parameters are enabled or true. (Legacy - prefer `paramIsTrue`)

    ```
    "onlyWhenTheseParams": ["Param1", "Param2"]

    ```

*   **`paramExists` / `paramNotExists`:** Checks if a parameter has a value.

    ```
    "paramExists": "DongleId"
    "paramNotExists": "SomeOptionalParam"

    ```

*   **`paramLocked` / `paramNotLocked`:** Checks if a parameter is locked (e.g., `ParamNameLock` is true).

    ```
    "paramLocked": "LateralTorqueFriction"
    "paramNotLocked": "SomeEditableParam"

    ```

*   **`isOffroad` / `isOnroad`:** Checks the vehicle's driving state.

    ```
    "isOffroad": true
    "isOnroad": true

    ```

*   **`isEngaged` / `isNotEngaged`:** Checks if openpilot is actively engaged.

    ```
    "isEngaged": true
    "isNotEngaged": true

    ```

*   **`isTiciHardware` / `isPcHardware`:** Checks the hardware platform.

    ```
    "isTiciHardware": true
    "isPcHardware": true

    ```

*   **`hasCarParams`:** Checks if car parameters are available.

    ```
    "hasCarParams": true

    ```

*   **`hasLongitudinalControl`:** Checks if the vehicle supports longitudinal control.

    ```
    "hasLongitudinalControl": true

    ```

*   **`isPcmCruise`:** Checks if the vehicle uses PCM cruise control.

    ```
    "isPcmCruise": true

    ```

*   **`hasBlindSpotMonitoring`:** Checks if blind spot monitoring is available.

    ```
    "hasBlindSpotMonitoring": true

    ```

*   **`isReleaseBranch` / `isNotReleaseBranch` / `isTestedBranch` / `isDevelopmentBranch`:** Branch type checks.

    ```
    "isReleaseBranch": true
    "isDevelopmentBranch": true

    ```


### Composite Conditions

Conditions can be combined using logical operators to form more complex criteria.

*   **`anyConditionsTrue`:** The control is visible if **any** of the specified conditions are true.

    ```
    "anyConditionsTrue": [
      { "paramValueEquals": { "DriveMode": "sport" } },
      { "allConditionsTrue": [ /* Nested conditions */ ] }
    ]

    ```

*   **`allConditionsTrue`:** The control is visible only if **all** of the specified conditions are true.

    ```
    "allConditionsTrue": [
      { "git_remote": ["ford-op/sp-dev-c3"] },
      { "paramValueLessThan": { "Temperature": 90 } }
    ]

    ```


**Example of Composite Conditions:**

```
{
  "conditions": {
    "anyConditionsTrue": [
      { "paramValueEquals": { "DriveMode": "sport" } },
      {
        "allConditionsTrue": [
          { "paramValueGreaterThan": { "Speed": 70 } },
          { "onlyWhenTheseParams": ["AdvancedModeEnabled"] }
        ]
      }
    ],
    "allConditionsTrue": [
      { "git_remote": ["ford-op/sp-dev-c3"] },
      { "paramValueLessThan": { "Temperature": 90 } }
    ]
  }
}
```

_In this example:_

*   The toggle is enabled if:
    *   **Any** of the following is true:
        *   `UserLevel` equals `"admin"`.
        *   Both:
            *   `SystemLoad` is greater than `70`.
            *   `SystemStable` is `true`.
    *   **And**:
        *   `git_remote` is `"ford-op/sp-dev-c3"`.
        *   `Temperature` is less than `90`.

## Examples

### Full Configuration Example

Below is a sample JSON configuration that defines multiple groups and controls, including various control types and conditions.

```
{
  "_comment": "This configuration file defines all Ford settings panels, groups, and controls.",
  "menuName": "BluePilot",
  "menuIcon": "icon_ford.png",
  "menuDescription": "BluePilot Panel",
  "persistentParams": [
    "FordSelectedVehicleModel",
    "FordPrefQuietDrive",
    "FordPrefEnableDebugLogs",
    "FordPrefSendHandsFreeCanMsg",
    "FordPrefLaneDepartCanMsg",
    "FordPrefDriverMonitorCanMsg",
    "FordPrefEnablePathAngle",
    "FordPrefHumanTurnDetectionEnable",
    "FordPrefEnableCustomLatLogic",
    "FordLatTuningLaneChgModifier",
    "FordLatTuningCustomPathOffset",
    "FordLongTuningBrakeActuatorActivate",
    "FordLongTuningBrakeActuatorReleaseDelta",
    "FordLongTuningPrechargeActuatorTargetDelta",
    "FordLimitsCurvatureMax",
    "FordLimitsCurvatureError"
  ],
  "clearOnManagerStartParams": [],
  "clearOnOnroadTransitionParams": [],
  "clearOnOffroadTransitionParams": [],
  "groups": [
    {
      "groupName": "vehicleSelectorGroup",
      "title": "Vehicle Selection: (Tap item for desc)",
      "enableResetButton": false,
      "controls": [
        {
          "type": "selection",
          "param": "FordSelectedVehicleModel",
          "title": "Vehicle Model",
          "desc": "Select your vehicle model",
          "disable": false,
          "hidden": false,
          "options": [
            { "name": "F-150 14th Gen (21-23)", "value": "FORD_F_150_MK14" },
            { "name": "F-150 Lightning 1st Gen", "value": "FORD_F_150_LIGHTNING_MK1" },
            { "name": "Mustang Mach-E 1st Gen", "value": "FORD_MUSTANG_MACH_E_MK1" }
          ]
        },
        {
          "type": "file_viewer",
          "path": "CHANGELOGS_BP.md",
          "title": "BluePilot Changelog",
          "desc": "View the BluePilot changelog",
          "header": "BluePilot Changelog",
          "disable": false,
          "hidden": false
        }
      ]
    },
    {
      "groupName": "systemPreferencesGroup",
      "title": "System Preferences: (Tap item for desc)",
      "enableResetButton": false,
      "controls": [
        {
          "type": "toggle",
          "param": "FordPrefEnableDebugLogs",
          "title": "Enable Debug Logging",
          "desc": "Enables additional debug output.",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        }
      ]
    },
    {
      "groupName": "clusterPreferencesGroup",
      "title": "Cluster Preferences: (Tap item for desc)",
      "enableResetButton": false,
      "controls": [
        {
          "type": "toggle",
          "param": "FordPrefSendHandsFreeCanMsg",
          "title": "Show Hands-Free UI (On Supported Vehicles)",
          "desc": "Sends necessary messages for Hands-Free interface.",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "toggle",
          "param": "FordPrefLaneDepartCanMsg",
          "title": "Send Lane Departure Signals to Vehicle",
          "desc": "Send Openpilot lane departure signals for native cluster alerts.",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "toggle",
          "param": "FordPrefDriverMonitorCanMsg",
          "title": "Send Driver Monitor Signals",
          "desc": "Send driver monitor notice signals to the vehicle for native cluster alerts.",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        }
      ]
    },
    {
      "groupName": "lateralControlsGroup",
      "title": "Lateral Controls: (Tap item for desc)",
      "enableResetButton": true,
      "controls": [
        {
          "type": "toggle",
          "param": "FordPrefHumanTurnDetectionEnable",
          "title": "Enable Human Turn Detection",
          "desc": "Reset steering so you don't fight the wheel making manual turns.",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "toggle",
          "param": "FordPrefAllowNudgelessLaneChange",
          "title": "Allow Nudgeless Lane Changes",
          "desc": "Allow nudgeless lane change",
          "disable": false,
          "hidden": false,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "segmented_control",
          "param": "FordLatTuningTuningProfile",
          "title": "Tuning Profile",
          "desc": "Sets the tuning aggressiveness",
          "disable": false,
          "hidden": false,
          "options": [
            { "name": "Low", "value": "1" },
            { "name": "Medium", "value": "2" },
            { "name": "High", "value": "3" },
            { "name": "Custom", "value": "4" }
          ],
          "defaultValue": "2",
          "conditions": {
            "allConditionsTrue": [
              { "git_remote": ["any"] },
              { "git_branch": [] }
            ]
          }
        },
        {
          "type": "float",
          "param": "FordLatTuningCustomPathOffset",
          "title": "In Lane Offset",
          "desc": "Positions car further left (negative) or right (positive)",
          "disable": false,
          "hidden": false,
          "min": -0.5,
          "max": 0.5,
          "increment": 0.05,
          "division": 100.0,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLatTuningPCBlendRatioUI",
          "title": "Predicted Curvature Blend Ratio",
          "desc": "Sets the blend ratio between predicted and desired curvature",
          "disable": false,
          "hidden": false,
          "min": 0.0,
          "max": 1.0,
          "increment": 0.01,
          "division": 100.0,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLatTuningPathAngleHighSpeedFactorUI",
          "title": "Path Angle High Speed Factor",
          "desc": "Lower numbers for less twitchy steering",
          "disable": false,
          "hidden": false,
          "min": 0.0,
          "max": 10.0,
          "increment": 0.01,
          "division": 100.0,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLatTuningPathAngleHighCurvatureFactorUI",
          "title": "Path Angle High Curvature Factor",
          "desc": "Lower numbers for less aggressive curves",
          "disable": false,
          "hidden": false,
          "min": 0.0,
          "max": 1.0,
          "increment": 0.05,
          "division": 100.0,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLatTuningLaneChangeFactorHighUI",
          "title": "Lane Change Factor",
          "desc": "Lower numbers for less aggressive lane change",
          "disable": false,
          "hidden": false,
          "min": 0.0,
          "max": 1.0,
          "increment": 0.05,
          "division": 100.0,
          "conditions": {
            "git_remote": ["any"],
            "git_branch": []
          }
        }
      ]
    },
    {
      "groupName": "brakeTuningGroup",
      "title": "Brake Tuning: (Tap item for desc)",
      "enableResetButton": true,
      "controls": [
        {
          "type": "float",
          "param": "FordLongTuningBrakeActuatorActivate",
          "title": "Brake Actuator Activate",
          "desc": "Acceleration setpoint for brake actuator activation.",
          "disable": false,
          "hidden": false,
          "min": -0.2,
          "max": 0.2,
          "increment": 0.01,
          "division": 100.0,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLongTuningBrakeActuatorReleaseDelta",
          "title": "Brake Actuator Release Delta",
          "desc": "Acceleration gap between activation and release.",
          "disable": false,
          "hidden": false,
          "min": 0.0,
          "max": 0.2,
          "increment": 0.01,
          "division": 100.0,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLongTuningPrechargeActuatorTargetDelta",
          "title": "Precharge Actuator Target Delta",
          "desc": "How much earlier to activate the precharge actuator.",
          "disable": false,
          "hidden": true,
          "min": 0.0,
          "max": 0.2,
          "increment": 0.01,
          "division": 100.0,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        }
      ]
    },
    {
      "groupName": "limitsTuningGroup",
      "title": "Limits Tuning: (Tap item for desc)",
      "enableResetButton": true,
      "controls": [
        {
          "_comment": "Originally commented out in the code snippet",
          "type": "float",
          "param": "FordLimitsCurvatureMax",
          "title": "Curvature Max",
          "desc": "Defines the max curvature allowed.",
          "disable": false,
          "hidden": true,
          "min": 0.0,
          "max": 0.2,
          "increment": 0.005,
          "division": 100.0,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        },
        {
          "type": "float",
          "param": "FordLimitsCurvatureError",
          "title": "Curvature Error",
          "desc": "Defines the max curvature error allowed.",
          "disable": false,
          "hidden": true,
          "min": 0.0,
          "max": 0.02,
          "increment": 0.001,
          "division": 1000.0,
          "conditions": {
            "git_remote": ["ford-op/sp-dev-c3"],
            "git_branch": []
          }
        }
      ]
    },
    {
      "groupName": "paramViewerGroup",
      "title": "Parameter Viewer",
      "enableResetButton": false,
      "controls": [
        {
          "type": "param_viewer",
          "param": "LiveParameters",
          "title": "Live Parameters",
          "desc": "View live parameters",
          "disable": false,
          "hidden": false
        }
      ]
    },
    {
      "groupName": "bpInfoGroup",
      "title": "Other Information",
      "enableResetButton": false,
      "controls": [
        {
          "type": "file_viewer",
          "path": "CHANGELOGS_BP.md",
          "title": "BluePilot Changelog",
          "desc": "View the BluePilot changelog",
          "header": "BluePilot Changelog",
          "disable": false,
          "hidden": false
        }
      ]
    }
  ]
}
```

### Individual Control Examples

#### Toggle Control with Conditions

This example demonstrates a toggle control that is only available when the Git remote is `ford-op/sp-dev-c3`.

```
{
  "type": "toggle",
  "param": "FordPrefEnableDebugLogs",
  "title": "Enable Debug Logging",
  "desc": "Enables additional debug output.",
  "disable": false,
  "hidden": false,
  "conditions": {
    "git_remote": ["ford-op/sp-dev-c3"],
    "git_branch": []
  }
}
```

#### Float Control with Default Value

This float control allows users to adjust the lane change modifier with a default value set to `2`.

```
{
  "type": "float",
  "param": "FordLatTuningLaneChgModifier",
  "title": "Lane Change Modifier",
  "desc": "Adjust lane change curvature aggressiveness (lower = slower).",
  "disable": false,
  "hidden": false,
  "min": 0.0,
  "max": 1.0,
  "increment": 0.05,
  "division": 100.0,
  "conditions": {
    "git_remote": ["any"],
    "git_branch": []
  }
}
```

#### Command Button Control with Confirmation

This command button control executes a system update command with confirmation and action buttons that appear based on the command result.

```json
{
  "type": "command_button",
  "command": "/data/openpilot/scripts/system_update.sh",
  "working_dir": "/data/openpilot",
  "command_timeout_ms": 600000,
  "title": "System Update",
  "desc": "Updates the system to the latest version with automatic rollback on failure",
  "button_text": "Update Now",
  "confirm": true,
  "confirm_text": "This will update your system. Continue?<br><br><b>Note:</b> The process may take several minutes.",
  "confirm_button_text": "Yes, Update",
  "cancel_button_text": "Cancel",
  "showRetry": true,
  "actionButtons": [
    {
      "text": "Reboot Device",
      "action": "reboot",
      "showWhen": "success",
      "confirm": true,
      "confirm_text": "Update completed successfully. Reboot now to apply changes?",
      "confirm_yes_text": "Reboot Now",
      "confirm_no_text": "Later"
    },
    {
      "text": "View Logs",
      "command": "tail -n 50 /data/openpilot/update.log",
      "showWhen": "failure",
      "confirm": false
    }
  ],
  "disable": false,
  "hidden": false
}
```

_In this example:_
- The "Reboot Device" button only appears when the update succeeds (`showWhen: "success"`)
- The "View Logs" button only appears when the update fails (`showWhen: "failure"`)
- Both buttons have appropriate actions for their respective scenarios

#### Segmented Control Example

This segmented control allows users to select the tuning profile with predefined options.

```
{
  "type": "segmented_control",
  "param": "FordLatTuningTuningProfile",
  "title": "Tuning Profile",
  "desc": "Sets the tuning aggressiveness",
  "disable": false,
  "hidden": false,
  "options": [
    { "name": "Low", "value": "1" },
    { "name": "Medium", "value": "2" },
    { "name": "High", "value": "3" },
    { "name": "Custom", "value": "4" }
  ],
  "defaultValue": "2",
  "conditions": {
    "allConditionsTrue": [
      { "git_remote": ["any"] },
      { "git_branch": [] }
    ]
  }
}
```

#### Conditional Visibility Based on Parameter Values

This example demonstrates conditional visibility where different controls appear based on the value of another parameter. This uses `visibleConditions` to show/hide controls dynamically.

**Scenario:** Speed Limit Offset controls that change based on offset type (None/Fixed/Percent)

```
{
  "controls": [
    {
      "type": "segmented_control",
      "param": "SpeedLimitOffsetType",
      "title": "Speed Limit Offset",
      "desc": "Choose offset type",
      "options": [
        { "name": "None", "value": "0", "default": true },
        { "name": "Fixed", "value": "1" },
        { "name": "Percent", "value": "2" }
      ]
    },
    {
      "type": "integer",
      "param": "SpeedLimitValueOffset",
      "title": "Fixed Offset Value",
      "desc": "Fixed speed offset value in mph/km/h",
      "min": -30,
      "max": 30,
      "increment": 1,
      "unit": "mph",
      "visibleConditions": {
        "paramValueEquals": { "SpeedLimitOffsetType": "1" }
      }
    },
    {
      "type": "integer",
      "param": "SpeedLimitValueOffset",
      "title": "Percent Offset Value",
      "desc": "Percent speed offset value",
      "min": -30,
      "max": 30,
      "increment": 1,
      "unit": "%",
      "visibleConditions": {
        "paramValueEquals": { "SpeedLimitOffsetType": "2" }
      }
    }
  ]
}
```

_In this example:_

*   When `SpeedLimitOffsetType` is set to `"0"` (None):
    *   Both integer controls are hidden
*   When `SpeedLimitOffsetType` is set to `"1"` (Fixed):
    *   The "Fixed Offset Value" control becomes visible with "mph" unit
    *   The "Percent Offset Value" control remains hidden
*   When `SpeedLimitOffsetType` is set to `"2"` (Percent):
    *   The "Percent Offset Value" control becomes visible with "%" unit
    *   The "Fixed Offset Value" control remains hidden

**Key advantages of `visibleConditions`:**
- Controls are completely hidden when not applicable (cleaner UI)
- Multiple controls can share the same parameter with different visibility rules
- User only sees relevant controls for their current selection
- No need for composite `allConditionsTrue` wrapper when using single conditions

#### Advanced Condition Example

This example demonstrates the use of both `paramValueEquals` and `anyConditionsTrue` to control the visibility and behavior of a control based on multiple criteria.

```
{
  "type": "toggle",
  "param": "FordAdvancedFeatureEnable",
  "title": "Enable Advanced Feature",
  "desc": "Enables the advanced feature based on multiple conditions.",
  "disable": false,
  "hidden": false,
  "conditions": {
    "anyConditionsTrue": [
      { "paramValueEquals": { "UserLevel": "admin" } },
      {
        "allConditionsTrue": [
          { "paramValueGreaterThan": { "SystemLoad": 70 } },
          { "onlyWhenTheseParams": ["SystemStable"] }
        ]
      }
    ],
    "allConditionsTrue": [
      { "git_remote": ["ford-op/sp-dev-c3"] },
      { "paramValueLessThan": { "Temperature": 90 } }
    ]
  }
}
```

_In this example:_

*   The toggle is enabled if:
    *   **Any** of the following is true:
        *   `UserLevel` equals `"admin"`.
        *   Both:
            *   `SystemLoad` is greater than `70`.
            *   `SystemStable` is `true`.
    *   **And**:
        *   `git_remote` is `"ford-op/sp-dev-c3"`.
        *   `Temperature` is less than `90`.

## Optional vs. Required Properties

Understanding which properties are mandatory and which are optional is crucial for creating valid configurations.

### Required Properties

*   **Top-Level:**
    *   `menuName`
    *   `menuIcon`
    *   `menuDescription`
    *   `groups`
*   **Group Object:**
    *   `groupName`
    *   `title`
    *   `controls`
*   **Control Object:**
    *   `type`
    *   `param`
    *   `title`
    *   `desc`

### Optional Properties

*   **Top-Level:**
    *   `persistentParams`
    *   `clearOnManagerStartParams`
    *   `clearOnOnroadTransitionParams`
    *   `clearOnOffroadTransitionParams`
*   **Group Object:**
    *   `enableResetButton`
    *   `type` (if using special group types like `"tabPanel"`)
*   **Control Object:**
    *   `disable`
    *   `hidden`
    *   `conditions`
    *   Additional properties specific to control types (e.g., `min`, `max`, `options`, `increment`, `division`, `defaultValue`).

## Notes and Best Practices

*   **Unique `groupName`:** Ensure each `groupName` is unique across the configuration to prevent conflicts.
*   **Consistent Parameter Naming:** Use clear and consistent naming conventions for parameters (`param`) to maintain readability and manageability.
*   **Condition Accuracy:** When defining conditions, ensure that parameter names and expected values match existing configurations and logic to prevent controls from being unintentionally hidden or disabled.
*   **Increment and Division Values:** For float controls, `increment` and `division` values should be chosen carefully to balance precision and usability.
*   **Command Safety:** When using `command_button` controls, ensure that commands are safe and tested to prevent unintended system behavior.
*   **Styling Consistency:** Leverage the available styling options to maintain a consistent and intuitive UI across all controls and groups.
*   **Default Values:** Provide `defaultValue` where applicable to ensure controls have sensible initial states.
*   **Hidden Controls:** Use the `hidden` property to manage the visibility of controls based on their relevance or experimental status.
*   **Composite Conditions:** Utilize composite conditions to create complex visibility and behavior rules, enhancing the dynamic nature of the UI.

## Conclusion

The JSON configuration system for `ConfigDrivenPanel` offers a flexible and powerful way to define and manage user interface panels, groups, and controls. By adhering to the outlined structure and best practices, you can create customized, conditionally-driven interfaces that enhance the user experience and streamline configuration management.

For further customization and advanced configurations, refer to the codebase and explore additional properties and control types as needed.
