#!/bin/bash

cd "$(dirname "$0")"
. global_settings.sh

tests_total=0
tests_failed=0

for i in *.test
do
	unset cmd args input expected_output

	echo "Running '$i'."
	. "$i"

	# Note: Do NOT use "echo -n" here because "$input" misses a final
	# newline.
	diff -u \
		<(echo "$expected_output") \
		<(echo "$input" | "${cmd[@]}")
	(( tests_failed += $? ))
	(( tests_total++ ))
done
echo "fail $tests_failed, pass $((tests_total - tests_failed)),\
 total $tests_total"
[[ $tests_failed -eq 0 ]] # else, set the exit code
