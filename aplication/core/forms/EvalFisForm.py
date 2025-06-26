from django import forms
from aplication.core.models import EvaluacionFisica
from mysite.const import SEX_CHOICES, MAX_FILE_SIZE, ERROR_MESSAGES

class EvaluacionFisicaForm(forms.ModelForm):
    GENDER_CHOICES = [('', 'Selecciona')] + list(SEX_CHOICES)
    
    altura = forms.FloatField(
        label='Altura (cm)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ej. 175',
            'min': '100',
            'max': '250'
        }),
        required=True
    )
    
    peso = forms.FloatField(
        label='Peso (kg)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ej. 70',
            'min': '30',
            'max': '200'
        }),
        required=True
    )
    
    genero = forms.ChoiceField(
        label='Sexo',
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True
    )

    class Meta:
        model = EvaluacionFisica
        # Incluimos imagen y objetivo del modelo, más los campos adicionales
        fields = ['imagen', 'objetivo']
        widgets = {
            'imagen': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-white hover:file:bg-gray-600',
                'accept': 'image/*'
            }),
            'objetivo': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
        labels = {
            'imagen': 'Subir Imagen Corporal',
            'objetivo': 'Objetivo',
        }
        help_texts = {
            'imagen': 'Sube una foto para evaluar tu composición corporal.',
            'objetivo': 'Elige tu meta: perder grasa, tonificar, etc.',
        }

    def clean_altura(self):
        altura = self.cleaned_data.get('altura')
        if altura and (altura < 100 or altura > 250):
            raise forms.ValidationError('La altura debe estar entre 100 y 250 cm')
        return altura

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if peso and (peso < 30 or peso > 200):
            raise forms.ValidationError('El peso debe estar entre 30 y 200 kg')
        return peso

    def clean_genero(self):
        genero = self.cleaned_data.get('genero')
        if not genero:
            raise forms.ValidationError('Debes seleccionar un género')
        return genero

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            # Validar tamaño de archivo
            if imagen.size > MAX_FILE_SIZE:
                raise forms.ValidationError(
                    ERROR_MESSAGES['archivo_grande'].format(
                        max_size=MAX_FILE_SIZE / (1024 * 1024)
                    )
                )
            
            # Validar que no esté vacío
            if imagen.size == 0:
                raise forms.ValidationError(ERROR_MESSAGES['archivo_vacio'])
                
        return imagen

    def clean(self):
        cleaned_data = super().clean()
        # Aquí puedes agregar validaciones adicionales que involucren múltiples campos
        altura = cleaned_data.get('altura')
        peso = cleaned_data.get('peso')
        
        if altura and peso:
            # Ejemplo: validar IMC razonable
            imc = peso / ((altura/100) ** 2)
            if imc < 10 or imc > 50:
                raise forms.ValidationError('Los valores de altura y peso parecen inconsistentes')
        
        return cleaned_data
