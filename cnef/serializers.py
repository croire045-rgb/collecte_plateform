from rest_framework import serializers
from .models import (
    Etablissement, FichierImport, Credit_Amortissables, 
    Decouverts, Affacturage, Cautions, Effets_commerces, Spot
)


class EtablissementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etablissement
        fields = ['id', 'Nom_etablissement', 'type_etablissement', 'code_etablissement']


class FichierImportSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    total_lignes = serializers.IntegerField(source='total_lignes_importees', read_only=True)
    
    class Meta:
        model = FichierImport
        fields = [
            'id', 'etablissement', 'etablissement_nom', 'fichier', 'nom_fichier',
            'date_import', 'statut', 'nb_credits_importes', 'nb_decouverts_importes',
            'nb_affacturages_importes', 'nb_cautions_importes', 'nb_effets_importes',
            'total_lignes', 'erreurs', 'details'
        ]
        read_only_fields = [
            'date_import', 'statut', 'nb_credits_importes', 'nb_decouverts_importes',
            'nb_affacturages_importes', 'nb_cautions_importes', 'nb_effets_importes',
            'erreurs', 'details'
        ]


class CreditAmortissableSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    
    class Meta:
        model = Credit_Amortissables
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DecouvertSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    
    class Meta:
        model = Decouverts
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AffacturageSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    
    class Meta:
        model = Affacturage
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CautionSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    
    class Meta:
        model = Cautions
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EffetCommerceSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source='etablissement.Nom_etablissement', read_only=True)
    
    class Meta:
        model = Effets_commerces
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Serializers pour les imports
class ImportFichierSerializer(serializers.Serializer):
    fichier = serializers.FileField()
    etablissement_id = serializers.IntegerField()
    
    def validate_fichier(self, value):
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Seuls les fichiers Excel (.xlsx, .xls) sont autorisés")
        return value


class ResultatImportSerializer(serializers.Serializer):
    credits_importes = serializers.IntegerField()
    decouverts_importes = serializers.IntegerField()
    affacturages_importes = serializers.IntegerField()
    cautions_importes = serializers.IntegerField()
    effets_importes = serializers.IntegerField()
    total_lignes = serializers.IntegerField()
    erreurs = serializers.ListField(child=serializers.CharField())
    statut = serializers.CharField()