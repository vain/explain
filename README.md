explain
=======

This script allows you to explain commands using ASCII art. For example,
the following file:

	vim -p .bashrc .vimrc
	--- -- --------------

	Open the editor.

	Open the files in tabs.

	Which files to open?

Will result in:

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

Result:

	sed 's/hurz/herz/;p;q' < file
	\_/  |\____/\___/||||  \____/
	 |   |   |    |  ||||     |
	 |   |   |    |  ||||     \- Read from this file. The shell will handle
	 |   |   |    |  ||||        the redirection.
	 |   |   |    |  ||||
	 |   |   |    |  |||\- Quit.
	 |   |   |    |  |||
	 |   |   |    |  ||\- Another separator.
	 |   |   |    |  ||
	 |   |   |    |  |\- Print.
	 |   |   |    |  |
	 |   |   |    |  \- Separator.
	 |   |   |    |
	 |   |   |    \- ... with herz.
	 |   |   |
	 |   |   \- ... hurz ...
	 |   |
	 |   \- Replace ...
	 |
	 \- Run sed.

Usually, all adjacent lines of comments will be merged into one single
line. After that, it'll get wrapped to a given length. This means, that
manual line breaks will be lost. On the other hand, you may *want* to
place manual line breaks. To do so, end a line with two backslashes:

	Number 1
	------ -

	This is a very long line. There's a lot of text. It'll get wrapped
	automatically. Also note that there's line breaks inside of this
	comment. They'll be removed. This is the "traditional" way of handling
	comments.

	1: One! \\
	2: Two! \\
	3: Three! \\
	Now I added '\\' at the ends of those lines.
	That line, however, had no '\\' at its end. So, these two lines will
	become one single line and get wrapped properly.

And this is what you get:

	Number 1
	\____/ |
	   |   \- 1: One!
	   |      2: Two!
	   |      3: Three!
	   |      Now I added '\\' at the ends of those lines. That line,
	   |      however, had no '\\' at its end. So, these two lines will
	   |      become one single line and get wrapped properly.
	   |
	   \- This is a very long line. There's a lot of text. It'll get wrapped
	      automatically. Also note that there's line breaks inside of this
	      comment. They'll be removed. This is the "traditional" way of
	      handling comments.

See `./explain.py --help` for more parameters. You can alter the symbols
used in the graph with `-P` , for example.

You can explain several commands in one single source file.


Test cases
----------

There's a basic test suite available that can be run as follows:

	$ cd ~/git/explain/tests
	$ ./suite.sh

A test case is a short Bash script whose filename must end with `.test`:

	# Complete command line. This is a Bash array.
	cmd=("$program" '-P' 'unicode')

	# Notes:
	# - These here-documents don't have a final newline on the very last
	#   line. Hence, the "echo" calls in "suite.sh" must NOT add a "-n".

	read -rd '' input <<"EOF"
	ed .profile
	-- --------
	Editor.

	File to edit.
	EOF

	read -rd '' expected_output <<"EOF"
	ed .profile
	│  └───┬──┘
	│      │
	│      └ File to edit.
	│
	└ Editor.
	EOF

As you can see, it consists of three variables:

* `cmd`: The complete command line as a Bash array.
* `input`: The input that is fed to `explain.py`.
* `expected_output`: What `explain.py` must print for the test to
  succeed.

Furthermore, there's a file called `global_settings.sh`. In this file,
`$program` is defined.
