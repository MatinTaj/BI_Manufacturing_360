(SqlText as text) as table =>
    PostgreSQL.Database(pServer, pDatabase,
        [Query=SqlText, CreateNavigationProperties=false,
         CommandTimeout=#duration(0,0,2,0)])
