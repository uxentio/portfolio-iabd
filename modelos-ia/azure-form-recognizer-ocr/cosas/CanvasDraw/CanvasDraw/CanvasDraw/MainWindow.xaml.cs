using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace CanvasDraw
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            LoadImage();
        }

        private void LoadImage()
        {
            // Consigue el directorio de trabajo actual
            string currentDir = Environment.CurrentDirectory;
            // Crea la ruta al archivo de imagen en la subcarpeta 'Data'
            string imagePath = System.IO.Path.Combine(currentDir, "Data", "carnet_conducir.jpg");

            // Crea un Uri con la ruta absoluta
            Uri imageUri = new Uri(imagePath, UriKind.Absolute);

            // Carga la imagen y suscribe al evento Loaded
            imageControl.Source = new BitmapImage(imageUri);
            imageControl.Loaded += ImageControl_Loaded;
        }

        private void ImageControl_Loaded(object sender, RoutedEventArgs e)
        {
            DrawRectangles(); // Llama a DrawRectangles después de que la imagen esté cargada
        }

        private void DrawRectangles()
        {
            // Valores de ejemplo para las coordenadas X
            double[] xCoords = { 10, 150, 300 }; // Ajusta estos valores según tus coordenadas
            double height = 50; // Altura del rectángulo
            double width = 100; // Ancho del rectángulo

            foreach (double x in xCoords)
            {
                Rectangle rect = new Rectangle
                {
                    Stroke = Brushes.Red,
                    StrokeThickness = 2,
                    Height = height,
                    Width = width
                };
                Canvas.SetLeft(rect, x);
                Canvas.SetTop(rect, 50); // Ajusta esto para cambiar la posición vertical de los rectángulos
                canvasDraw.Children.Add(rect);
            }
        }
    }
}
