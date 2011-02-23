#!/bin/sh

myexplain() {
	echo '*************** running explain' "$@" :
	python ./explain.py "$@"
}

EXPLAIN=myexplain
. ./tests.inc > tests.output.actual
diff -u tests.output.supposed tests.output.actual
exit $?
