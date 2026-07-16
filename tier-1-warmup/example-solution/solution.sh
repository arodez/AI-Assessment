#!/bin/sh

# Default file paths
INPUT_FILE="data/engineers.csv"
OUTPUT_FILE="pending.txt"

# 1. Handle missing file
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: '$INPUT_FILE' not found." >&2
    exit 1
fi

# 2. Handle empty file or header-only file
LINE_COUNT=$(wc -l < "$INPUT_FILE" | tr -d ' ')
if [ "$LINE_COUNT" -eq 0 ] || [ "$LINE_COUNT" -eq 1 ]; then
    HEADER=$(head -n 1 "$INPUT_FILE" 2>/dev/null)
    if [ -z "$HEADER" ]; then
        echo "Error: CSV file is empty or has no headers." >&2
        exit 1
    else
        echo "No data rows found."
        exit 0
    fi
fi

# 3. Create/clear the output file
> "$OUTPUT_FILE"

# 4. Use awk to process fields and print counts.
# We then use sort externally to maintain portability across BSD (macOS) and GNU (Linux) environments.
awk -F',' '
BEGIN {
    skipped = 0;
    pending_count = 0;
}
NR == 1 {
    # Verify header columns contain "email" and "course_status"
    if ($2 != "email" || $3 != "course_status") {
        print "Error: CSV headers do not match expected format." > "/dev/stderr";
        exit 2;
    }
    next;
}
{
    # Trim leading/trailing whitespace
    gsub(/^[ \t]+|[ \t]+$/, "", $2);
    gsub(/^[ \t]+|[ \t]+$/, "", $3);
    
    # Check if row is missing status column entirely or is blank
    if (NF < 3 || $3 == "") {
        skipped++;
        next;
    }
    
    status = tolower($3);
    counts[status]++;
    
    if (status == "pending") {
        if ($2 != "") {
            print $2 > "pending.txt";
            pending_count++;
        }
    }
}
END {
    # Print counts to be sorted
    for (status in counts) {
        print "COUNT:  " status ": " counts[status];
    }
    
    if (skipped > 0) {
        print "SKIPPED:  skipped (malformed rows): " skipped;
    }
    
    print "WROTE:" pending_count;
}
' "$INPUT_FILE" > .awk_result.tmp

# Check if awk script failed on headers
AWK_EXIT=$?
if [ $AWK_EXIT -eq 2 ] || [ $AWK_EXIT -ne 0 ]; then
    rm -f .awk_result.tmp
    exit 1
fi

echo "Status counts:"
# Sort status counts alphabetically and print them
grep "^COUNT:" .awk_result.tmp | sed 's/^COUNT://' | sort
# Print skipped row counts if any
grep "^SKIPPED:" .awk_result.tmp | sed 's/^SKIPPED://'

PENDING_COUNT=$(grep "^WROTE:" .awk_result.tmp | cut -d':' -f2)
rm -f .awk_result.tmp

echo ""
echo "Wrote $PENDING_COUNT pending email(s) to '$OUTPUT_FILE'"
