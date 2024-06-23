# message_md

Code to hold `Message`s and convert them to Markdown.
 
Also includes all the supporting classes for `Person`, `Group`, `Setting`, `String`, `Config`, `Attachments` so the client code only needs to deal with the app-specific parsing of message files.

## Configuration

Read the [guide](docs/guide.md) to learn how to configure the library.

## Command line options

Any app that uses this library will inherit these command line options.

**IMPORTANT**: by default the begining date for the parsing is today so that it's easier (and faster) to get results and make sure everything is workling because you only have to look at a day's worth of messages. Once you're ready to parse everything, use something like `-b 1970-01-01` to get all the messages.

Argument | Alternate | Description
---|---|---
`-c` | `--config` | Folder where the configuration files are
`-s` | `--sourceFolder` | Folder where the message file is
`-f` | `--file` | The filename of the file containing all of the messages to be converted
`-o` | `--outputFolder` | Where the resulting Markdown files will go
`-l` | `--language` | UI language, defaults to English
`-m` | `--mySlug` | Which person in the config file is me e.g. `bob`
`-d` | `--debug` | Print debug messages
`-b` | `--begin` | The date from which to start converting
`-i` | `--imap` | IMAP server address
`-r` | `--folders` | IMAP folders to retrieve from
`-e` | `--email` | email address to retrieve from
`-p` | `--password` | email password
`-x` | `--max` | The maximum number of messages to process
`-a` | `--add` | Add people to the output even if not in `people.json` config file

 ## License

 Apache License 2.0
