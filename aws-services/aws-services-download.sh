#!/bin/bash

BASE_URL="https://aws.amazon.com/api/dirs/items/search"
COMMON_PARAMS="item.directoryId=products-cards-interactive-aws-products-ams&item.locale=en_US&tags.id=GLOBAL%23local-tags-aws-products-type%23service%7CGLOBAL%23local-tags-aws-products-type%23feature&sort_by=item.additionalFields.title&sort_order=asc"

PAGE_SIZE=24
TOTAL_ITEMS=264

# Calculate total pages
TOTAL_PAGES=$(( (TOTAL_ITEMS + PAGE_SIZE - 1) / PAGE_SIZE ))

echo "Total pages: $TOTAL_PAGES"

OUTPUT_FILE="aws_services.json"
> $OUTPUT_FILE   # clear file

for ((page=0; page<=TOTAL_PAGES-1; page++))
do
  echo "Fetching page $page..."

  curl -s "${BASE_URL}?${COMMON_PARAMS}&size=${PAGE_SIZE}&page=${page}" \
    -H "accept: application/json" \
    -H "user-agent: Mozilla/5.0" \
    >> $OUTPUT_FILE

  echo "" >> $OUTPUT_FILE   # newline separator

  sleep 1  # avoid rate limiting
done

echo "✅ Download complete: $OUTPUT_FILE"