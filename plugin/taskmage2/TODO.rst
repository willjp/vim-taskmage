* `taskmage2.api` defines commands used by vim. continue.

    * `api.handle_presave_mtask()` works with info available in buffer.
      This is not sufficient. must include JSON data for `created` `finished` etc.

    * tests for `data.Node.touch()`

    * tests for `parser.render(touch=True)`
