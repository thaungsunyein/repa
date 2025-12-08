-- Create user_criteria table
CREATE TABLE IF NOT EXISTS user_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    location TEXT,
    min_rooms INTEGER,
    max_rooms INTEGER,
    min_living_space DECIMAL(10, 2),
    max_living_space DECIMAL(10, 2),
    min_rent DECIMAL(10, 2),
    max_rent DECIMAL(10, 2),
    occupants INTEGER,
    duration TEXT,
    starting_when TEXT,
    user_additional_requirements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_criteria_user_id ON user_criteria(user_id);

-- Enable Row Level Security
ALTER TABLE user_criteria ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own criteria
CREATE POLICY "Users can view own criteria"
    ON user_criteria FOR SELECT
    USING (auth.uid() = user_id);

-- Create policy: Users can insert their own criteria
CREATE POLICY "Users can insert own criteria"
    ON user_criteria FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update their own criteria
CREATE POLICY "Users can update own criteria"
    ON user_criteria FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can delete their own criteria
CREATE POLICY "Users can delete own criteria"
    ON user_criteria FOR DELETE
    USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_user_criteria_updated_at
    BEFORE UPDATE ON user_criteria
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


