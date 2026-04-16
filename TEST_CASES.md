# AI Real Estate Agent - Test Cases

## Frontend Chat Functionality Test Cases

### Test Case 1: Complete Property Description
**Scenario**: User provides all necessary information in initial query
**Input**: "3 bedroom, 2 bathroom house built in 2005 with 1800 sqft living area, 10000 sqft lot, 2-car garage, excellent condition and quality, gas heating, central air, in NAmes neighborhood"
**Expected Behavior**:
- AI extracts all features correctly
- Shows extracted features with icons
- Immediately calculates price without asking questions
- Displays price result with explanation

### Test Case 2: Minimal Property Description (Original Bug Scenario)
**Scenario**: User provides minimal information, triggering question flow
**Input**: "3-bedroom house in NAmes"
**Expected Behavior**:
1. AI extracts bedrooms=3, neighborhood="NAmes", basement="None"
2. Shows extracted features FIRST (no delay)
3. Says "I need 9 more details to give you an accurate estimate. Let's go through them one by one:"
4. Asks for missing fields one by one with progress indicator (1/9, 2/9, etc.)
5. User answers all questions
6. Calculates price successfully (no "Missing 1 features" error)
7. Displays result

### Test Case 3: Partial Information with Retry Logic
**Scenario**: Backend reports additional missing fields after user input
**Input**: "3 bedroom house"
**Expected Behavior**:
1. AI shows extracted features (if any)
2. Says "I need X more details to give you an accurate estimate. Let's go through them one by one:"
3. Asks questions for missing fields
4. User answers all questions
5. If backend still reports missing fields, shows "I still need X more detail(s): [fields]. Let's continue:" and continues asking remaining questions
6. Eventually calculates price successfully

### Test Case 4: Invalid Input Validation
**Scenario**: User provides invalid responses to questions
**Input**: "3 bedroom house in NAmes"
**Then Answer**: "invalid" to numeric questions
**Expected Behavior**:
- Shows error message with ❌ icon
- Re-asks the same question
- Accepts valid input and continues

### Test Case 5: Garage Capacity Edge Cases
**Scenario**: Testing garage parsing logic
**Inputs**:
- "no garage" → should parse to 0
- "2" → should parse to 2
- "huge" → should show validation error
**Expected Behavior**: Correct parsing or appropriate error messages

### Test Case 6: Categorical Field Validation
**Scenario**: Testing basement and other categorical fields
**Input**: "3 bedroom house in NAmes"
**Then Answer**: "invalid_basement" to basement question
**Expected Behavior**:
- Accepts valid values: Ex, Gd, TA, Fa, Po, None
- Shows validation error for invalid values

### Test Case 7: UX Improvements Verification
**Scenario**: Verify progress tracking and message ordering
**Input**: Any query requiring multiple questions
**Expected Behavior**:
- Messages appear in correct order: extracted features → intro message → first question
- Progress indicators show (1/5), (2/5), etc.
- Friendly messages with emojis
- Smooth transitions between questions

### Test Case 8: Error Handling - Backend Unavailable
**Scenario**: Backend server is not running
**Input**: Any query
**Expected Behavior**:
- Shows error message: "❌ Error connecting to the valuation service. Please make sure the backend is running."
- Graceful degradation

### Test Case 9: Chat Reset Functionality
**Scenario**: User clicks "New Chat" button
**Input**: After completing a conversation, click "New Chat"
**Expected Behavior**:
- Clears all messages
- Resets chat state
- Shows initial centered icon
- Ready for new conversation

### Test Case 10: Long Conversation with Multiple Retries
**Scenario**: Complex scenario with backend reporting missing fields multiple times
**Input**: Minimal query, then provide answers that somehow still result in missing fields
**Expected Behavior**:
- Continues asking questions without getting stuck
- Preserves previously answered questions
- Eventually completes successfully

## Backend API Test Cases

### Test Case 11: Complete Override Features
**API Call**:
```json
{
  "query": "3 bedroom house",
  "override_features": {
    "bedrooms": 3,
    "bathrooms": 2.0,
    "sqft_living": 1800,
    "sqft_lot": 10000,
    "year_built": 2005,
    "garage_cars": 2,
    "condition": 8,
    "quality": 7,
    "neighborhood": "NAmes",
    "basement": "TA",
    "heating": "GasA",
    "central_air": "Y"
  }
}
```
**Expected Response**: `status: "complete"` with price prediction

### Test Case 12: Incomplete Override Features
**API Call**:
```json
{
  "query": "3 bedroom house",
  "override_features": {
    "bedrooms": 3,
    "bathrooms": 2.0
  }
}
```
**Expected Response**: `status: "incomplete"` with missing_fields list

### Test Case 13: Invalid Override Features
**API Call**:
```json
{
  "query": "3 bedroom house",
  "override_features": {
    "bedrooms": "three",
    "bathrooms": 2.0
  }
}
```
**Expected Response**: `status: "error"` with validation message

### Test Case 14: Natural Language Only
**API Call**:
```json
{
  "query": "beautiful 4 bedroom colonial in StoneBr neighborhood",
  "override_features": null
}
```
**Expected Response**: LLM extracts features, returns complete or incomplete status

## Integration Test Cases

### Test Case 15: End-to-End Complete Flow
1. User enters complete query
2. Frontend sends to backend
3. Backend returns complete prediction
4. Frontend displays result
5. User can start new chat

### Test Case 16: End-to-End Incomplete Flow
1. User enters incomplete query
2. Frontend sends to backend
3. Backend returns incomplete status with extracted features and missing fields
4. Frontend shows extracted features FIRST (synchronously)
5. Frontend shows "I need X more details..." message SECOND
6. Asks questions one by one THIRD
7. User answers all questions
8. Frontend sends complete override_features
9. Backend returns prediction
10. Frontend displays result

### Test Case 17: Error Recovery Flow
1. User enters query
2. Backend temporarily unavailable
3. Frontend shows error
4. User retries
5. Flow completes successfully

## Performance Test Cases

### Test Case 18: Response Time
**Scenario**: Measure time from user input to price display
**Expected**: < 5 seconds for complete queries, < 10 seconds for incomplete flows

### Test Case 19: Memory Usage
**Scenario**: Multiple conversations without page refresh
**Expected**: No memory leaks, chat state properly reset

## Accessibility Test Cases

### Test Case 20: Keyboard Navigation
**Scenario**: Navigate chat using only keyboard
**Expected**: Tab through elements, Enter to send, proper focus management

### Test Case 21: Screen Reader Compatibility
**Scenario**: Use screen reader to interact with chat
**Expected**: Proper ARIA labels, semantic HTML, readable content