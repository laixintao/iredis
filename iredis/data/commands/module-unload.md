Unloads a module.

This command unloads the module specified by `name`. Note that the module's name
is reported by the `MODULE LIST` command, and may differ from the dynamic
library's filename.

Known limitations:

- Modules that register custom data types can not be unloaded.

@return

@simple-string-reply: `OK` if module was unloaded.
