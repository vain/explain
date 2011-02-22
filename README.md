explain
=======

This script allows you to explain commands using ASCII art. For example,
the following file:

	vim -p .bashrc .vimrc
	--- -- --------------

	Open the editor.

	Open the files in tabs.

	Which files to open?

When fed into `explain` will result in:

	vim -p .bashrc .vimrc
	\_/ |  \____________/
	 |  |         |
	 |  |         \- Which files to open?
	 |  |
	 |  \- Open the files in tabs.
	 |
	 \- Open the editor.

You can use a `+` to end two adjacent ranges. Furthermore, a `!` will
assign a comment to one single character. A more complex example:

	sed 's/hurz/herz/;p;q' < file
	---  !-----+-----!!!!  ------

	Run sed.

	Replace ...

	... hurz ...

	... with herz.

	Separator.

	Print.

	Another separator.

	Quit.

	Read from this file. The shell will handle the redirection.

Note that a `+` is optional if followed by a `!`.

Result when piped through `explain -P rounded`:

	sed 's/hurz/herz/;p;q' < file
	╰┬╯  │╰──┬─╯╰─┬─╯││││  ╰──┬─╯
	 │   │   │    │  ││││     │
	 │   │   │    │  ││││     ╰ Read from this file. The shell will handle
	 │   │   │    │  ││││       the redirection.
	 │   │   │    │  ││││
	 │   │   │    │  │││╰ Quit.
	 │   │   │    │  │││
	 │   │   │    │  ││╰ Another separator.
	 │   │   │    │  ││
	 │   │   │    │  │╰ Print.
	 │   │   │    │  │
	 │   │   │    │  ╰ Separator.
	 │   │   │    │
	 │   │   │    ╰ ... with herz.
	 │   │   │
	 │   │   ╰ ... hurz ...
	 │   │
	 │   ╰ Replace ...
	 │
	 ╰ Run sed.

See `./explain --help` for more parameters. You can alter the symbols
used in the graph with `-P` , for example.

You can explain several commands in one single source file.
