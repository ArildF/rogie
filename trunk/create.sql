CREATE TABLE FaqAliases
(
    Alias Text Unique Primary Key,
    CanonicalName Text    
);

CREATE TABLE FaqVersions
(
    Id Integer Primary Key,
    Name Text,
    Version Int,
    State Int,
    Contents Text,
    Created TimeStamp Not Null,
    Author Text Not Null
);

CREATE TABLE LatestVersion
(
    Name Text Primary Key,
    Id Int
);