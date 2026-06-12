# API Verification Commands

Quick-reference curl commands to verify each business API key works.
Source env first: `source ~/.hermes/.env 2>/dev/null`

## Meta Business (Facebook/Instagram)

```bash
# Verify user identity
curl -s "https://graph.facebook.com/v21.0/me?access_token=${META_PAGE_TOKEN}"
# → {"name":"...","id":"..."}

# List pages with permissions
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token=${META_PAGE_TOKEN}"
# → data[].{name, id, category, tasks[]}

# Check granted permissions
curl -s "https://graph.facebook.com/v21.0/me/permissions?access_token=${META_PAGE_TOKEN}"
# → data[].{permission, status}

# Get page details (use PAGE_ID from /accounts response)
curl -s "https://graph.facebook.com/v21.0/{PAGE_ID}?fields=name,fan_count,followers_count,link&access_token=${META_PAGE_TOKEN}"
```

## Lemon Squeezy (Payments)

```bash
curl -s -H "Authorization: Bearer ${LEMON_SQUEEZY_API_KEY}" \
  "https://api.lemonsqueezy.com/v1/users/me"
# → data.attributes.name

# List stores
curl -s -H "Authorization: Bearer ${LEMON_SQUEEZY_API_KEY}" \
  "https://api.lemonsqueezy.com/v1/stores"

# List products (NOTE: products are READ-ONLY via API, create in dashboard)
# IMPORTANT: URL-encode brackets! filter[x] → filter%5Bx%5D
curl -s -H "Authorization: Bearer ${LEMON_SQUEEZY_API_KEY}" \
  -H "Accept: application/vnd.api+json" \
  'https://api.lemonsqueezy.com/v1/products?filter%5Bstore_id%5D=STORE_ID'

# List discounts (discounts CAN be created via API unlike products)
curl -s -H "Authorization: Bearer ${LEMON_SQUEEZY_API_KEY}" \
  -H "Accept: application/vnd.api+json" \
  'https://api.lemonsqueezy.com/v1/discounts?filter%5Bstore_id%5D=STORE_ID'

# Create a discount (POST works for discounts)
curl -s -X POST -H "Authorization: Bearer ${LEMON_SQUEEZY_API_KEY}" \
  -H "Content-Type: application/vnd.api+json" \
  -H "Accept: application/vnd.api+json" \
  'https://api.lemonsqueezy.com/v1/discounts' \
  -d '{"data":{"type":"discounts","attributes":{"name":"CODE","code":"CODE","amount":20,"amount_type":"percent"},"relationships":{"store":{"data":{"type":"stores","id":"STORE_ID"}}}}}'
```

## Mailchimp (Email Marketing)

```bash
# Datacenter from key suffix: b079...0f-us10 → us10
curl -s --user "anystring:${MAILCHIMP_API_KEY}" \
  "https://us10.api.mailchimp.com/3.0/"
# → {account_name, email, total_subscribers, ...}

# List audiences
curl -s --user "anystring:${MAILCHIMP_API_KEY}" \
  "https://us10.api.mailchimp.com/3.0/lists"

# List tags for a list
curl -s --user "anystring:${MAILCHIMP_API_KEY}" \
  "https://us10.api.mailchimp.com/3.0/lists/LIST_ID/segments?type=static"

# Create a tag
curl -s -X POST --user "anystring:${MAILCHIMP_API_KEY}" \
  -H "Content-Type: application/json" \
  "https://us10.api.mailchimp.com/3.0/lists/LIST_ID/segments" \
  -d '{"name":"tag-name","static_segment":[]}'

# Update list settings (from_name, from_email, subject)
curl -s -X PATCH --user "anystring:${MAILCHIMP_API_KEY}" \
  -H "Content-Type: application/json" \
  "https://us10.api.mailchimp.com/3.0/lists/LIST_ID" \
  -d '{"campaign_defaults":{"from_name":"Name","from_email":"email@example.com","subject":"Welcome"}}'
```

## ElevenLabs (TTS)

```bash
curl -s -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  "https://api.elevenlabs.io/v1/user"
# → subscription tier, character usage
```

## Canva (Design) — OAuth Required

Keys stored but need OAuth browser flow to get access token.
Client ID + Secret alone can't verify. Need to complete:
1. Authorization URL → user grants access → redirect with code
2. Exchange code for access_token

## TikTok (Social) — OAuth Required

Same as Canva — client key/secret need OAuth flow.
