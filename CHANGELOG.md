# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [In Development] - Unreleased

## [1.1.0]
Fixed bugs:
- Menu dropdown items expand outside the canvas
- Navbar doubles it's size on some resolutions
- No link to the markdown guide on the navbar
- Search doesn't work on menus (and sections) available for everyone
- PyPI doesn't install app_utils automatically
- Clicking on fontawesome link when creating/changing a new section doesn't open a new tab
- Clicking on the fontawesome links shows all icons, free and premium
- Icon names are required to be formatted as "fas fa-<name>"
- Editor dropdown menus don't show which menu is active

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