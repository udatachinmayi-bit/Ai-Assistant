# Database

Persistence layer. `models/` holds ORM/schema definitions, `migrations/` holds schema version migrations. Consumed only through repository interfaces, never via raw queries scattered across modules.
