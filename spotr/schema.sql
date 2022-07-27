DROP TABLE IF EXISTS ListenedTrack;                -- Deletes table if exists!!!
DROP TABLE IF EXISTS ToListenTrack;
DROP TABLE IF EXISTS WatchList;
DROP TABLE IF EXISTS WatchListNewTracks;
DROP TABLE IF EXISTS FavoriteTrack;
DROP TABLE IF EXISTS LikedTrack;

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

CREATE TABLE ToListenTrack (
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
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_time_checked TIMESTAMP NOT NULL,
    no_of_items_checked INTEGER,
    href TEXT,
    list_of_current_items TEXT, -- try to store list as string: https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    imageURL TEXT,
    new_items_since_last_check INTEGER  
);

CREATE TABLE WatchListNewTracks (
    id TEXT PRIMARY KEY,    -- id of sole entry = "newTracks"
    trackList TEXT  -- list of dicts: {"id": track id, "from_type": from playlist? from artist?, "from_name": name of playlist/artist/..}  -- try to store list as string: https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
);

CREATE TABLE FavoriteTrack(
    id TEXT PRIMARY KEY,
    spotify_id TEXT,
    album TEXT,
    artists TEXT,
    title TEXT,
    href TEXT,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    times_searched INTEGER
);

CREATE TABLE LikedTrack(   --contains all tracks that are in 'like tracks' list in spotify 20220211
    id TEXT PRIMARY KEY,
    album TEXT,
    artists TEXT,
    title TEXT,
    href TEXT,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    times_searched INTEGER
);