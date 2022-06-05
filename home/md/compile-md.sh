#!/bin/bash

m4_include(stdlib.m4)m4_dnl
emit_dir=".."
css_path=bojle_css_path
base_name="$(basename "$1" | cut -d . -f 1)"
emit_file="$emit_dir"/"$base_name".html
md2html -f "$1" > "$emit_file"
sed -i "/<title>/a <link rel=\"stylesheet\" href=\"$css_path\">" "$emit_file" 
