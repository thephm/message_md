# message-md

Code to hold `Message`s and convert them to Markdown.
 
Also includes all the supporting classes for `Person`, `Group`, `Setting`, `String`, `Config`, `Attachments` so the client code only needs to deal with the app-specific parsing of message files.

## Command line options

Any app that uses this library will inherit these command line options.

Argument | Alternate | Description
---|---|---
`-c` | `--config` | Folder where the configuration files are
`-s` | `--sourceFolder` | Folder where the message file is
`-f` | `--file` | The file containing all of the messages to be converted
`-o` | `--outputFolder` | Where the resulting Markdown files will go
`-l` | `--language` | UI language, defaults to English
`-m` | `--mySlug` | Which person in the config file is me e.g. `bob`
`-d` | `--debug` | Print debug messages
`-b` | `--begin` | The date from which to start converting

 ## License

 Apache License 2.0
