# 🐛 Debug Guide: Start Search Button

## Current Changes (Version 3.1)

I've added comprehensive debugging and improved the button reactivity:

### 1. **Computed Signal for Button State**
```typescript
isButtonDisabled = computed(() => {
  const query = this.searchQuery();
  const processing = this.isProcessing();
  return !query || query.trim().length === 0 || processing;
});
```

### 2. **Debug Logging**
The component now logs to the browser console:
- Initial state on component load
- Every keystroke in the textarea
- Button disabled state after each change

### 3. **Dual Input Handling**
```typescript
(ngModelChange)="onQueryInput($event)"
(input)="onQueryInput($any($event.target).value)"
```

## How to Debug

1. **Open the page**: `http://localhost:4200/conversations`

2. **Open Browser DevTools**:
   - Press `F12` or `Cmd+Option+I` (Mac)
   - Go to the **Console** tab

3. **Watch the console as you type**:
   ```
   💬 ConversationsComponent initialized - Version 3.0 (Zoneless)
   🔍 Initial searchQuery: 
   🔍 Initial isButtonDisabled: true
   
   [After typing "test":]
   📝 Query input changed: t
   🔍 Query length: 1
   🔍 Is button disabled? false
   ```

4. **Check the button state**:
   - Initially: Button should be **grayed out** (disabled)
   - After typing 1+ characters: Button should be **purple** (enabled)
   
5. **Test the button**:
   - Type: "hello"
   - The button should become clickable
   - Click it to send the query to the backend

## If Button is Still Not Working

### Check Browser Console for:
1. **Any errors** (red messages)
2. **The debug logs** showing the button state
3. **Network requests** when you click the button

### Try:
1. **Hard refresh**: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
2. **Clear browser cache**
3. **Try in an incognito window**

### Check the Backend:
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy",...}`

## What Should Happen

1. **Type in textarea** → Signal updates → Computed signal recalculates → Button enables
2. **Click button** → `executeSearch()` called → POST to `http://localhost:8000/api/agent/chat`
3. **Response received** → Displayed below the search box

## Technical Notes

- Using **computed signals** for better reactivity
- **Zoneless change detection** requires explicit signal updates
- Both `ngModelChange` and `input` events to ensure all input methods work
- Debug logging helps trace the reactive flow

---
Last Updated: November 21, 2025

