def subscribers_favorites_shopping_cart(self, obj, qs):
    user = self.context['request'].user
    if user.is_anonymous:
        return False
    return obj.qs.filter(subscriber=user).exists()
