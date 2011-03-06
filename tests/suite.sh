#!/bin/bash

cd "$(dirname "$0")"
. global_settings.sh

for i in *.test
do
	unset cmd args input expected_output

	echo "Running '$i'."
	. "$i"

	# Note: Do NOT use "echo -n" here because "$input" misses a final
	# newline.
	diff -u \
		<(echo "$input" | "${cmd[@]}") \
		<(echo "$expected_output")
done
