
service Adder {
    add(a, b)
    @precondition {{ a > 0 and b > 0 }}
    @postcondition {{ result == a + b }}
}
