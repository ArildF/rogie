CREATE TABLE FaqAliases
(
    Alias Text Unique Primary Key COLLATE NOCASE ,
    CanonicalName Text COLLATE NOCASE    
);

CREATE TABLE FaqVersions
(
    Id Integer Primary Key,
    Name Text COLLATE NOCASE,
    Version Int,
    State Int,
    Contents Text COLLATE NOCASE,
    Created TimeStamp Not Null,
    Author Text Not Null COLLATE NOCASE
);

CREATE TABLE LatestVersion
(
    Name Text Primary Key COLLATE NOCASE,
    Id Int
);

CREATE TABLE Quotes
(
    Id Integer Primary Key,
    Contents Text COLLATE NOCASE,
    Author Text COLLATE NOCASE,
    Created TimeStamp Not Null,
    AddingUser Text COLLATE NOCASE    
);