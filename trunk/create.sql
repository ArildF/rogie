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
    Author Text Not Null,
    Created TimeStamp Not Null,
    PRIMARY KEY( Name, Version )
);

CREATE TABLE LatestVersion
(
    Name Text Primary Key,
    Version Int
);