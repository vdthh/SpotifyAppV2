DROP TABLE IF EXISTS ListenedTrack;
DROP TABLE IF EXISTS WatchList;
DROP TABLE IF EXISTS NewWatchListTracks;

CREATE TABLE ListenedTrack (
    id TEXT PRIMARY KEY,
    spotify_id TEXT,
    album TEXT,
    artists TEXT,
    title TEXT,
    href TEXT,
    popularity INTEGER,
    from_playlist TEXT,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    how_many_times_double INTEGER
);

CREATE TABLE WatchList (
    id TEXT PRIMARY KEY,
    _type TEXT,
    _name TEXT,
    date_added TEXT,
    last_time_checked TEXT,
    no_of_items_checked INTEGER,
    href TEXT,
    list_of_current_items TEXT, -- try to store list as string: https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    imageURL TEXT,
    new_items_since_last_check INTEGER
);

CREATE TABLE NewWatchListTracks (
    id TEXT PRIMARY KEY,
    trackList TEXT
);
