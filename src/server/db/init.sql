-- Synced from backend 0.1.0.dev1
CREATE TABLE users (
	addional_fields JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE general_blobs (
	blob_type VARCHAR(255) NOT NULL, 
	blob_data JSONB NOT NULL, 
	user_id UUID NOT NULL, 
	addional_fields JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
