
# 9. Set up PostgreSQL user and database
# sudo -i -u postgres psql <<EOF
-- Create a new PostgreSQL user
 # CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create a new PostgreSQL database
# CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant all privileges on the database to the new user
# GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Exit the PostgreSQL prompt
# EOF

# echo "PostgreSQL setup completed: user '$DB_USER' with database '$DB_NAME' has been created."

# echo "Python, PostgreSQL, and requirements installation completed successfully!"
echo "~/.local/bin has been added to your PATH. Please log out and log back in, or run 'source ~/.profile' to apply the changes."
