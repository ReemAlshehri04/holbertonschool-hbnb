-- data.sql

-- Insert Admin User (Note: Use a placeholder or hashed password as per your logic)
INSERT INTO Users (id, first_name, last_name, email, password, is_admin)
VALUES ('36c90530-802a-4384-9097-f87532320a02', 'Admin', 'HBnB', 'admin@hbnb.com', 'hashed_admin_password', 1);

-- Insert Default Amenities
INSERT INTO Amenities (id, name) VALUES 
('10b6d214-9989-4e00-84e9-026857a2e8e3', 'WiFi'),
('20c7e325-0090-5f11-95f0-137968b3f9f4', 'Swimming Pool'),
('30d8f436-1101-6g22-06g1-248079c4g0g5', 'Air Conditioning'),
('40e9g547-2212-7h33-17h2-359180d5h1h6', 'Gym');
