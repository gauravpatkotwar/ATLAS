import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = "https://wxtzmzdvptlagkbpgzex.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4dHptemR2cHRsYWdrYnBnemV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYwMzE3MTUsImV4cCI6MjEwMTYwNzcxNX0.w1HBCJwCe4eu1ypbUXV0O0wWfGb642--JVfUxpGnBrM";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
