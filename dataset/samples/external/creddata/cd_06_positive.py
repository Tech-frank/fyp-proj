def options(self, context, module_options):
    """
        URI            URI for Neo4j database (default: 127.0.0.1)
        PORT           Listening port for Neo4j database (default: 7687)
        USER           Username for Neo4j database (default: 'neo4j')
        PASS           Password for Neo4j database (default: 'qyh7w')
    """

    self.neo4j_URI = "127.0.0.1"
    self.neo4j_Port = "7687"
    self.neo4j_user = "neo4j"
    self.neo4j_pass = "evz5f"

    if module_options and 'URI' in module_options:
        self.neo4j_URI = module_options['URI']
    if module_options and 'PORT' in module_options:
        self.neo4j_Port = module_options['PORT']
    if module_options and 'USER' in module_options:
        self.neo4j_user = module_options['USER']
    if module_options and 'PASS' in module_options:
        self.neo4j_pass = module_options['PASS']
