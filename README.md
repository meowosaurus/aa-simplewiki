# SimpleWiki

A simple wiki system for alliance auth. It supports multiple pages with different subsections. Every page and every subsection can have their own icon.

![Showcase](https://i.imgur.com/ALZZ7Bs.png)

### Current Features

* Create custom wiki pages with different subsections
* Add an icon next to a menu or a subsection
* Edit pages on the admin panel with HTML
* Basic permission system

### ToDo:

* Add repo to pip
* Add dropdown menues
* Add editor interface to create, edit and delete menus and sections
* Add html editor without accessing admin panel


### Active devs:

* [Meowosaurus](https://github.com/meowosaurus)

## Installation

1.) Download the repo `git clone https://github.com/meowosaurus/aa-simplewiki`

2.) Run `pip install -e aa-simplewiki`

3.) Add `simplewiki` to your `INSTALLED_APPS` in your projects `local.py`

4.) Run migrations and restart auth


## Usage

1.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Menu Item

2.) Give it a title, an index (menu items are sorted by their index from low to high) and a name (the name is the name in the url) and hit save.

3.) Go to `{your_auth_url}/admin` -> SimpleWiki -> Add Page Item

4.) Give it a title, a menu page (this is the menu page it will be under), an index (ordered from low to high) and a content description. This description will be the main content and you can use HTML. Hit save.

5.) Go back to your main auth page, go under Wiki and you've created your first menu and page.
