
def register_routes(app):
    from app.routes.auth import auth_bp
    from app.routes.cards import cards_bp
    from app.routes.collections import collections_bp
    from app.routes.decks import decks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(decks_bp)