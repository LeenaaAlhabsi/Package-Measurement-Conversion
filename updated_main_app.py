def char_to_value(c):
    if c == '_':
        return 0
    if 'a' <= c <= 'z':
        return ord(c) - ord('a') + 1
    raise ValueError(f"Invalid character '{c}' in input string")

def to_value_list(s: str):
    """Convert string to value list, handling 'z' special case."""
    L = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == 'z':
            total = 0
            while i < n and s[i] == 'z':
                total += char_to_value(s[i])
                i += 1
            if i < n:
                total += char_to_value(s[i])
                i += 1
            L.append(total)
        else:
            L.append(char_to_value(s[i]))
            i += 1
    return L

def parse(s: str):
    """Process value list with two-pointer grouping logic."""
    values = to_value_list(s)
    result = []
    i = 0
    n = len(values)
    while i < n:
        count = values[i]
        i += 1
        seg_sum = 0
        for _ in range(count):
            if i < n:
                seg_sum += values[i]
                i += 1
        result.append(seg_sum)
    return result

# ---------------- Main Test Entry ----------------
if __name__ == "__main__":
    test_inputs = [
        "dz_a_aazzaaa",                      # Expected output: [26,53,1]
        "aa",                                # Expected output: [1]
        "abbcc",                             # Expected output: [2,6]
        "a",                                 # Expected output: [0]
        "abcdabcdab",                        # Expected output: [2,7,7]
        "abcdabcdab_",                       # Expected output: [2,7,7,0]
        "zdaaaaaaaabaaaaaaaabaaaaaaaabbaa",  # Expected output: [34]
        "zza_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_",  # Expected output: [26]
        "za_a_a_a_a_a_a_a_a_a_a_a_a_azaaa"     # Expected output: [40,1]
    ]
    for t in test_inputs:
        print("Input:", t)
        print("Output:", parse(t))