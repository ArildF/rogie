CREATE TABLE FaqAliases
(
    Alias Text Unique Primary Key,
    CanonicalName Text    
);

CREATE TABLE FaqVersions
(
    Name Text,
    Version Int,
    State Int,
    Contents Text,
    Author Text,
    PRIMARY KEY( Name, Version )
);