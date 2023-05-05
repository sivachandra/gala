asm(".pushsection \".debug_gdb_scripts\", \"MS\",%progbits,1\n" \
    ".byte 1\n" \
    ".asciz \"autoload_test/autoload_this_gdb.py\"\n" \
    ".popsection\n");

asm(".pushsection \".debug_gdb_scripts\", \"MS\",%progbits,1\n" \
    ".byte 1\n" \
    ".asciz \"autoload_test/excluded_script.py\"\n" \
    ".popsection\n");

asm(".pushsection \".debug_gala_lldb_scripts\", \"MS\",%progbits,1\n" \
    ".byte 1\n" \
    ".asciz \"autoload_test/autoload_this_lldb.py\"\n" \
    ".popsection\n");

asm(".pushsection \".debug_gdb_scripts\", \"MS\",%progbits,1\n" \
    ".byte 4\n" \
    ".ascii \"autoload_test_embedded_script\\n\"\n" \
    ".ascii \"import sys\\n\"\n" \
    ".ascii \"print('Hi from embedded script!', file=sys.stderr)\\n\"\n" \
    ".byte 0\n" \
    ".popsection\n");

int main() { return 0; }
