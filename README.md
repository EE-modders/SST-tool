# Empire Earth tools for the SST image format

#### what is this?

this is a SST and TGA libary combined with new tools for modding the Empire Earth SST image / texture format in order to replace the SST converter of the EE Studio software

## Included software

### SSTtool

This software allows you to convert SST image files into TGA and vice versa.
All the image tiles and resolutions included in the SST file will be extracted and can be packed back into SST.

### SSTviewer

A simple viewer for SST image files

## How to use it?

Download the latest version of the software you want from the [releases](https://github.com/EE-modders/SST-tool/releases) page.

In order to convert or open the file, you just Drag&Drop the file(s) onto the executable.

You can also use the CLI interface via a terminal.

The software runs standalone and no installation is needed. 

For further help and documentation you can go to the [wiki pages](https://github.com/EE-modders/SST-tool/wiki).

#### Supported games

- Empire Earth (CD)
- Empire Earth AoC (addon)
- Empire Earth Gold Edition (GOG)

**important:** Empire Earth DOMW **will not work**

## Contribute

- if you have an issue or suggestion feel free to create an [issue](https://github.com/EE-modders/SST-tool/issues) or [pull request](https://github.com/EE-modders/SST-tool/pulls) 
- you can also join our official [EE-reborn Discord server](https://discord.gg/BjUXbFB).

#### why this and not EE Studio?

EE Studio is a great (and up until now) the only software that allows to convert SST images into a more usable format.

Unfortunately we've discovered, that the resulting TGA and / or SST files are not only very big, but also lack important information, which get lost during the conversion process.

A SST-file can contain multiple images tiles and / or resolutions, which get lost when using EE Studio and thus are not moddable.

Furthermore EE Studio was not able to convert images bigger than the original file, which made creating new high(er) resolution textures nearly impossible.

**SSTtool** solves both problems and allows all tiles and resolutions of a SST-texture to be extracted.
