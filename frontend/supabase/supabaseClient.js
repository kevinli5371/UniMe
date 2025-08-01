// frontend/supabase/supabaseClient.js
import { createClient } from '@supabase/supabase-js';

// Use the actual values since your env variables aren't working
const supabaseUrl = 'https://ecgogrjlydaaqdklaims.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjZ29ncmpseWRhYXFka2xhaW1zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM5OTk1OTUsImV4cCI6MjA2OTU3NTU5NX0.1a6hxuRHt45XyQTS9Ut9fOn000QrwEMUwDUyo4YdS5U';

export const supabase = createClient(supabaseUrl, supabaseKey);