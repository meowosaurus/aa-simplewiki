# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## Released

## [2.1.0]
New features:
- Added WYSIWYG editor 

Changes:
- The section modal now stores the HTML code, instead of markdown text.

Fixed bugs:
- Fixed a bug where creating a section without an index would result in an error.
- Fixed a bug where page contents texts wouldn't scale correctly with the window.
- Fxied a bug where images wouldn't scale correctly with the window.

## [2.0.3]
Fixed bugs:
- Fixed an internal error bug

## [2.0.2]
Fixed bugs:
- Fixed a bug that threw a no context error

## [2.0.1]
Fixed bugs:
- Removed a debugging logger

## [2.0.0]
New features:
- Support for Alliance Auth 4.0

Important:
- This update is no longer compatible with Alliance Auth 3.x

## [1.1.3]
New features:
- Added a page contents view to every wiki page
- Added a "last edited" info below the page contents
- Added option to display/hide page contents (SIMPLEWIKI_DISPLAY_PAGE_CONTENTS)

Fixed bugs:
- It's no longer possible to create no-name sections
- When creating a section, the index no longer gets overwritten by "0"

## [1.1.2]
Fixed bugs:
- When editing sections, the index will be reset to 0
- When opening a menu, the sections are not sorted

## [1.1.1]
- Made jquery locally available

## [1.1.0]
New features:
- Drag and drop system for rearranging menus
- Menus are now accessable by a user's state

Fixed bugs:
- Index page redirects now to first menu, not oldest menu
- Menu dropdown items no longer expand outside the screen
- Navbar no longer doubles it's size on some resolutions
- Add link on editor dropdown menu to the markdown guide
- Search now also lists public sections
- app_utils is now a PyPI requirement
- Fontawesome link now opens in a new tab
- Fontawesome link now only shows free icons (premium icons are not usable anyway)
- Icon names are no longer required to be formatted as "fas fa-<name>", you can either use the name, html or old format
- Editor dropdown menus now show which sub-menu is active

Internal Optimizations:
- Reworked the menu and section models
- Changed error code to error strings
- Add logging for helper functions

## [1.0.5]
New minor features:
- Added support for tables 
- Added support for alerts
- Added support for google drive
- Added markdown reference guide at https://{auth.your_domain_here}/wiki/editor/guides/markdown

Behind the scenes:
- Added basic logging

## [1.0.4]
New minor features:
- Added support for YouTube and Vimeo videos 
  - `youtube:<id>:<width>:<height>`
  - `vimeo:<id>:<width>:<height>`
  - `width` and `height` are optional
- Added support to add a hyperlink to links automatically

Behind the scenes:
- Removed `commonmark`
- Added `mistune`

## [1.0.3]
Fixed bug:
- Fixed a permission bug that prevented menus from showing even when no groups were selected.

## [1.0.2]
Fixed bug:
- Fixed a permission bug that prevented users from accessing a newly created menu that doesn't require any permissions.

## [1.0.1]
Fixed bugs:
- Fixed a bug where the parent menu gets reset when editing an existing menu
- Fixed a bug where the groups get reset when editing an existing menu

## [1.0.0]
This is the first major release of aa-simplewiki.

- Create custom wiki menus with dropdowns plus different sections on each menu
- Add an icon next to menus or sections
- Edit pages on the admin panel with [markdown](https://commonmark.org/help/)
- Search function: Search across all wiki menus and sections
- Permission system:
  - Editor permissions can be added to single users or groups via the admin panel
  - Alliance Auth groups are synced to simplewiki: Certain pages can only be seen by a specific group
  - Multiple groups support: As long as the user is in any of the required groups, they can access the menu
- Editor interface
  - Users with editor permission can create, edit and delete custom menus and sections (editor_access)
  - Users with editor permission see edit and delete buttons above all sections (editor_access)
- Plugin can be installed by cloning the repo, or using pip. Pip is the recommended way, as it is production ready.
