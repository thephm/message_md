# Guide

This file provides details on how to setup the `message_md` library's JSON configuration files.

There are a few files that you need to setup:

1. `people.json` - a row for each person you communicate with across all messaging platforms
2. `groups.json` - a collection of People
3. `settings.json` - controls how the tool generates the Markdown

## People

Add each of the people you communicate with into `config\people.json` file with each person defined on a separate row. 

### Fields

- `slug` - one-word or hyphenated-words uniquely identifying this person
- `first-name` - the person's first name
- `last-name` - the person's last name
- `ignore` - optional and `False` to include or `True` to exclude from the output
- `mobile` - the phone number field in the `signald` output file
- `linkedin-id` - the last part of their LinkedIn profile URL
- `conversation-id` - required for [signal_sqlite_md](https://github.com/thephm/signal_sqlite_md/tree/main)

### Example

```
[
{
    "slug":"spongebob",
    "first-name":"SpongeBob",
    "last-name":"SquarePants", 
    "mobile":"+14165551212", 
    "linkedin-id":"spbob", 
    "conversation-id": "1bd7281f-45b4-4e95-a638-a84af8743ec6"
}
{
    "slug":"mr-krabs",
    "first-name":"Eugene", 
    "first-name":"Krabs",
    "ignore": "True", 
    "mobile":"+12895551313", 
    "linkedin-id":"mrkrab", "conversation-id":"d84d84b4-41b8-4044-93a6-2b47cd347e25"}
]
```

## Groups

Add the groups that you are part of into `config\groups.json`. This is for Signal and SMS group messages, not yet for LinkedIn group chats.

### Fields

- `id` - the unique ID for this group, see [Finding the group ID](#finding-the-group-id)
- `slug` - a one-word label for the group, will be used as the folder name
- `people` - a comma-separated list of person slugs enclosed in `[]`
- `conversation-id` - required for `signal_sqlite_md` (optional)
 
### Finding the group ID

This is specific to [signal_md](https://github.com/thephm/signal_md) which uses `signald`, it's not relevant for SMS. If you're using [signal_sqlite_md](https://github.com/thephm/signal_sqlite_md), that repo's `README` describes how to find the IDs.

To find the unique group ID, search through the JSON output from `signald`.

First, send a message to the group in Signal so you can then search for it in the `signald` output.

Once you've sent a message, open the `signald` output and search for `groupV2` and right after that will be the `id` field of the group. This is the value to be placed in the `id` field.

#### Example

Here's a snippet of the output from `signald` with a number of attributes removed for readability sake.

```
{"type":"IncomingMessage",
   "data":{
        "source":{
          "data_message":{
            "groupV2":{
                "id":"G49mXaA6ZEo+EbSCwbU97yYnekOMtQZ8oEhXFDLy9sE=",
```

### Example

Below is an example of the `groups.json` config file with two groups `fishing` and `bikini-bottom`.

```
{
    "groups": [
        {
            "id":"G49mXaA6ZEo+EbSCwbU97yYnekOMtQZ8oEhXFDLy9sE=",
            "slug":"fishing",
            "description":"They get hooked!",
            "people": ["spongebob","patrick"]
        },
        {
            "id":"wPmRPSnq0hajafjtrzecYyod5T1v68hHjvW/ongRcUQ=",
            "slug":"bikini-bottom",
            "description":"Bikini Bottom residents",
            "people": ["spongebob", "mr-krabs", "patrick"]
        }
}
```

## Settings

Customize the format of the output in the settings file:

```
config\settings.json
``` 

### Language

The `language` setting controls which language the output strings will be in

- Set to `1` for English 

### My slug

The `my-slug` setting defines which person (row) represents you in `people.json`.

#### Example

If this was me in `people.json`:

```
{"person-slug":"spongebob","first-name":"SpongeBob", "last-name":"SquarePants", "number":"+14165551212", "linkedin-id":"spbob", "conversation-id": "1bd7281f-45b4-4e95-a638-a84af8743ec6"}
```

Then I would set this field as follows in `settings.json`:

```
"my-slug": "spongebob",
```

### Timestamp

The `include-timestamp` field controls whether the time that a message was sent is included in the Markdown output, or not.

#### Values

The possible settings:

- `0` - do **not** include the timestamp
- `1` - include the timestamp

#### Examples

If this field is set to `1`

```
10:20
```

### Include quote

If `include-quote` is set to `1`: 

```
> This is the message
```

If this field is set to `0`:

```
This is the message
```

#### Colon after content

If `colon-after-context` is set to `1`, then

```
SpongeBob at 10:20:
```

If this field is set to `0`, then

```
SpongeBob at 10:20
```

#### Time and name separate

The `time-name-separate` setting controls where the timestamp is written:

- `1` - time on a separate line before the person's name
- `0` - time on the same line as the name e.g. "Bob at 10:23"

## Strings

Each string used in file: 

```
conig\strings.json
``` 

#todo add other languages, none yet `1` for English

### Fields

The following are the fields in this JSON file.

- `language` - ID of the language
- `number` - unique string ID within a language
- `text` - the actual string

The `number` field must not be changed.

### Example

```
{"language":"1","number":"0","text":"string not found"}
{"language":"1","number":"1","text":"at"}
```

## Person and date together

The `time-name-separate` setting controls whether the time of the message and the person who sent the message are shown on the same line or separate lines.

### Values

- `0` - time and name on separate lines
- `1` - time and name on the same line

### Examples

If set to `0`, then the sender's first name and time are output like this: 

```
SpongeBob at 10:20
```

If set to `1`, then the the time is output, a blank line, and then the sender's first name.

```
10:20

SpongeBob 
```

## Include reactions

The `include-reactions` setting controls whether the emoji reactions that people make on messages are included in the output file. By default this is set to `0` (exclude reactions).

Set like this and **all reactions** will be included in the output file.

```
"include-reactions":1,
```

Set like this and **no reactions** will be included in the output file.

```
"include-reactions":0,
```

## Folders

### Source folder

The `source-folder` setting controls where the input `signalmd` JSON files are.

### Messages file

This is the name of the file containing the messages. The format of the file is specific to the client using this library and the client handles parsing this file. For example, in the case of `signal_md` it's JSON and in the case of `signal_sqlite_md` and `linkedin_md` it's CSV. The location of the file is defined in the `source-folder` setting.

### Attachments sub-folder

The `attachments-subfolder` is under the `source-folder` where the attachment files are. 

### Archive folder

The `archive-folder` is where a copy of the original messages file is placed so the messages don't get processed again.

### Output folder

The `output-folder` setting controls where the generated Markdown file(s) for **individual** conversations are placed. If this field is not in the settings file, default will be `output` where the script is run.

### Groups folder

The `groups-folder` setting controls where the generated Markdown file(s) for **group** conversations are placed. If this field is not in the settings file, default will be `output\groups` where the script is run.

### Media SubFolder

The `media-subfolder` controls where the media (e.g. images) are stored. 

- empty - same folder as messages
- a string in quotes - folder name 

If this field is not in the settings file, the default will be in the folder where the messages are logged.

Examples:

To place media files in a subfolder called `media`, use:

```
"media-subfolder": "media"
```

To place media files in same folder as the messages, use:

```
"media-subfolder": ""
```

### Image embed

The `image-embed` flag adds a `!` in front of the image link `[[]]` which will render the image in the output file when viewed in an app like Obsidian.

For example if the attachment file is `1997332635961492225` and it's a jpeg, the following Markdown will be generated:

```
![[media/1997332635961492225.jpg]]
```

### Image width

The `image-width` flag adds a `|x` inside of the image link `[[]]` which tells the Markdown editor to render the media in `x` pixels wide. This is supported in Obsidian and is handy so the media files e.g. images don't overtake the entire page when you're viewing it.

For example if this is set to `100`, the attachment file is `1997332635961492225`, and it's a jpeg, the following Markdown will be generated:

```
![[media/1997332635961492225.jpg|150]]
```

### Daily Notes folder

If `daily-notes-folder` is a non-empty string, then messages to yourself are appended to dated files in the daily notes folder.

## File per person

When set to `1` the `file-per-person` setting causes a separate file for each person to be created. All messages with that person are appended to the same file.

```
    "file-per-person":1,
```

## File per day

When set to `1` the `file-per-day` setting creates a separate file for each day using format `MM-DD-YYYY`>. All messages with that person on that day are appended to that file.

```
    "file-per-day":1,
```

## IMAP Server

The IMAP server from where to retrieve emails.

```
    "imap-server": "imap.fastmail.com",
```

## email account

The email account from which to retrieve emails.

```
    "email-account": "spongebob@fastmail.com",
```
     
## email folder(s)

A semicolon separated list of email folders from which to retrieve emails.

```
    "email-folder": "INBOX",
```

## Max messages

Sets the number of messages to convert.

```
    "max-messages": 100,
```

## Note to self

There's special handling for Note-to-Self:

- `<firstName at>` are never shown so those settings don't have any affect

