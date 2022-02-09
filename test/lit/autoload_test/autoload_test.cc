asm(".pushsection \".debug_gdb_scripts\", \"MS\",%progbits,1\n" \
    ".byte 1\n" \
    ".asciz \"autoload_test/autoload_this.py\"\n" \
    ".popsection\n");

int main() { return 0; }
