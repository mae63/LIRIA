-- Supabase Database Schema for LIRIA
-- Run this SQL in your Supabase SQL Editor to create the tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (managed by Supabase Auth, but we can add custom fields if needed)
-- Note: Supabase Auth automatically creates auth.users table

-- Library entries table
CREATE TABLE IF NOT EXISTS library_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT,
    categories TEXT[],
    source TEXT,
    raw_id TEXT,
    cover_url TEXT,
    rating INTEGER DEFAULT 0,
    comment TEXT,
    api_rating NUMERIC,
    api_ratings_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wishlist entries table
CREATE TABLE IF NOT EXISTS wishlist_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT,
    categories TEXT[],
    thumbnail TEXT,
    source TEXT,
    preview_link TEXT,
    book_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_library_entries_user_id ON library_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_entries_user_id ON wishlist_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Enable Row Level Security (RLS)
ALTER TABLE library_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own data
-- Drop existing policies if they exist (to allow re-running the script)
DROP POLICY IF EXISTS "Users can view their own library entries" ON library_entries;
DROP POLICY IF EXISTS "Users can insert their own library entries" ON library_entries;
DROP POLICY IF EXISTS "Users can update their own library entries" ON library_entries;
DROP POLICY IF EXISTS "Users can delete their own library entries" ON library_entries;

DROP POLICY IF EXISTS "Users can view their own wishlist entries" ON wishlist_entries;
DROP POLICY IF EXISTS "Users can insert their own wishlist entries" ON wishlist_entries;
DROP POLICY IF EXISTS "Users can delete their own wishlist entries" ON wishlist_entries;

DROP POLICY IF EXISTS "Users can view their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can insert their own conversations" ON conversations;

DROP POLICY IF EXISTS "Users can view their own messages" ON messages;
DROP POLICY IF EXISTS "Users can insert their own messages" ON messages;

-- Create policies
CREATE POLICY "Users can view their own library entries"
    ON library_entries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own library entries"
    ON library_entries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own library entries"
    ON library_entries FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own library entries"
    ON library_entries FOR DELETE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own wishlist entries"
    ON wishlist_entries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own wishlist entries"
    ON wishlist_entries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own wishlist entries"
    ON wishlist_entries FOR DELETE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own conversations"
    ON conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own conversations"
    ON conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own messages"
    ON messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own messages"
    ON messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );


