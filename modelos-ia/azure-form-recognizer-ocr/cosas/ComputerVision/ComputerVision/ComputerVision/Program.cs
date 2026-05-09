using Microsoft.Azure.CognitiveServices.Vision.ComputerVision;
using Microsoft.Azure.CognitiveServices.Vision.ComputerVision.Models;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace ComputerVisionQuickstart
	{
	/// <summary>
	///		Este ejemplo del SDK de Computer Vision hace uso de un conjutno
	///		de imágenes, que pueden ser locales o remotas, para ilustrar las
	///		siguientes características:
	///		
	///		- Análisis de una imagen 
	///		- Detección de objetos
	///		- Detección de contenido perteneciente a un dominio específico
	///		- Generación de miniaturas
	///		
	///		Las imágenes de ejemplo que se utilizan pueden descargarse en la 
	///		siguiente URL: 
	///			https://github.com/Azure-Samples/cognitive-services-sample-data-files/tree/master/ComputerVision/Images
	///		
	///		Es necesario referenciar el siguiente paquete NuGet:
	///			
	///			Microsoft.Azure.CognitiveServices.Vision.ComputerVision
	///			
	///		(en este ejemplo se	utiliza la version 7.0.1 prerelease)
	///		
	/// 
	/// </summary>
	class Program
		{
		const string SubscriptionKey = "APIKEY";
		const string Endpoint = "ENDPOINT";

		//static readonly string LocalImagePathForAnalysis = Path.Combine(Environment.CurrentDirectory, "Images", "celebrities.jpg");
		static readonly string LocalImagePathForDetection = Path.Combine(Environment.CurrentDirectory, "Images", "objects.jpg");
		static readonly string LocalImagePathForSpecificDomainDetection = Path.Combine(Environment.CurrentDirectory, "Images", "celebrities.jpg");
        private const string ImageUrlForAnalysis =
            "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/faces.jpg";

        private const string ImageUrlForDetection =
            "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/objects.jpg";

        private const string ImageUrlForSpecificiDomainDetectino =
            "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg";
        static void Main(string[] args)
			{
			Console.WriteLine("Ejemplo del SDK de Computer Vision");
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();

			ComputerVisionClient client = Authenticate(Endpoint, SubscriptionKey);

			// Analiza una imagen y extrae sus propiedades
			AnalyzeImageUrl(client, ImageUrlForAnalysis).Wait();

			// Detecta objetos en una imagen
			DetectObjectsUrl(client, ImageUrlForDetection).Wait();

			// Detecta contentido de un dominio específico
			DetectDomainSpecific(client, ImageUrlForSpecificiDomainDetectino, LocalImagePathForSpecificDomainDetection).Wait();

			// Generate a thumbnail image from a URL and local image
			GenerateThumbnail(client, ImageUrlForAnalysis, LocalImagePathForDetection).Wait();

			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine("Fin del programa.");
			Console.ReadLine();
			}

		public static ComputerVisionClient Authenticate(string endpoint, string key)
			{
			ComputerVisionClient client = new ComputerVisionClient
				(
				new ApiKeyServiceClientCredentials(key)
				)
				{
				Endpoint = endpoint
				};

			return client;
			}

		/// <summary>
		///		El análisis de imagen incluye la extracción de:
		///			- Títulos
		///			- Etiquetas
		///			- Categorías
		///			- Objetos
		///			- Caras
		///			- Contenido racista/para adultos/violento
		///			- Identificación de marcas comerciales
		///			- Identificación de personajes famosos.
		///			- Áreas de detección,
		///			- Esquema de colores
		///			- Tipo de imagen
		/// </summary>
		public static async Task AnalyzeImageUrl(ComputerVisionClient client, string imageUrl)
			{
			Console.WriteLine("ANÁLISIS DE IMAGEN");
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();

			// Crea una lista que contiene las características a extraer de la imagen
			List<VisualFeatureTypes?> features = new List<VisualFeatureTypes?>()
				{
				VisualFeatureTypes.Categories,
				VisualFeatureTypes.Description,
				VisualFeatureTypes.Faces,
				VisualFeatureTypes.ImageType,
				VisualFeatureTypes.Tags,
				VisualFeatureTypes.Adult,
				VisualFeatureTypes.Color,
				VisualFeatureTypes.Brands,
				VisualFeatureTypes.Objects
				};

			Console.WriteLine($"\tImagen analizada: {Path.GetFileName(imageUrl)}...");
			Console.WriteLine();

			// Para analizar una imagen local tendríamos un código similar al siguiente:
			//using (Stream analyzeImageStream = File.OpenRead(localImage))
			//	{
			//	ImageAnalysis results = await client.AnalyzeImageInStreamAsync(analyzeImageStream, visualFeatures: features);
			//	Console.WriteLine("Títulos:");
			//	...

			ImageAnalysis results = await client.AnalyzeImageAsync(imageUrl, visualFeatures: features);

			// Muestra los resultados del análisis
			Console.WriteLine("Títulos:");

			foreach (var caption in results.Description.Captions)
				{
				Console.WriteLine($"{caption.Text} con valor de confianza {caption.Confidence}");
				}
			Console.WriteLine();

			Console.WriteLine("Categorías:");
			foreach (var category in results.Categories)
				{
				Console.WriteLine($"{category.Name} con valor de confianza {category.Score}");
				}
			Console.WriteLine();

			Console.WriteLine("Etiquetas:");
			foreach (var tag in results.Tags)
				{
				Console.WriteLine($"{tag.Name} {tag.Confidence}");
				}
			Console.WriteLine();

			Console.WriteLine("Objects:");
			foreach (var obj in results.Objects)
				{
				Console.WriteLine($"{obj.ObjectProperty} con valor de  confianza {obj.Confidence} en la posición {obj.Rectangle.X}, " +
				  $"{obj.Rectangle.X + obj.Rectangle.W}, {obj.Rectangle.Y}, {obj.Rectangle.Y + obj.Rectangle.H}");
				}
			Console.WriteLine();

			Console.WriteLine("Caras:");

			foreach (var face in results.Faces)
				{
				Console.WriteLine($"Un hombre/mujer: {face.Gender} de edad: {face.Age} en la posición {face.FaceRectangle.Left}, " +
				  $"{face.FaceRectangle.Left}, {face.FaceRectangle.Top + face.FaceRectangle.Width}, " +
				  $"{face.FaceRectangle.Top + face.FaceRectangle.Height}");
				}

			Console.WriteLine();

			Console.WriteLine("Contenido racista, para adultos o violento:");

			Console.WriteLine($"Muestra contenido para adultos: {results.Adult.IsAdultContent} con valor de confianza {results.Adult.AdultScore}");
			Console.WriteLine($"Muestra contenido racista: {results.Adult.IsRacyContent} con valor de confianza {results.Adult.RacyScore}");
			Console.WriteLine($"Muestra contenido violento: {results.Adult.IsGoryContent} con valor de confianza {results.Adult.GoreScore}");
			Console.WriteLine();

			Console.WriteLine("Marcas comerciales:");
			foreach (var brand in results.Brands)
				{
				Console.WriteLine($"Logo of {brand.Name} con valor de confianza {brand.Confidence} en la posición{brand.Rectangle.X}, " +
				  $"{brand.Rectangle.X + brand.Rectangle.W}, {brand.Rectangle.Y}, {brand.Rectangle.Y + brand.Rectangle.H}");
				}
			Console.WriteLine();

			Console.WriteLine("Personalidades famosas:");
			foreach (var category in results.Categories)
				{
				if (category.Detail?.Celebrities != null)
					{
					foreach (var celeb in category.Detail.Celebrities)
						{
						Console.WriteLine($"{celeb.Name} con valor de confianza {celeb.Confidence} en la posición{celeb.FaceRectangle.Left}, " +
						  $"{celeb.FaceRectangle.Top}, {celeb.FaceRectangle.Height}, {celeb.FaceRectangle.Width}");
						}
					}
				}
			Console.WriteLine();

			Console.WriteLine("Puntos de referencia:");
			foreach (var category in results.Categories)
				{
				if (category.Detail?.Landmarks != null)
					{
					foreach (var landmark in category.Detail.Landmarks)
						{
						Console.WriteLine($"{landmark.Name} con valor de confianza {landmark.Confidence}");
						}
					}
				}
			Console.WriteLine();

			Console.WriteLine("Esquema de colores:");
			Console.WriteLine("¿Blanco y negro?: " + results.Color.IsBWImg);
			Console.WriteLine("Color incidente: " + results.Color.AccentColor);
			Console.WriteLine("Color predominante en segundo plano: " + results.Color.DominantColorBackground);
			Console.WriteLine("Color predominante en primer plano: " + results.Color.DominantColorForeground);
			Console.WriteLine("Colores predominantes: " + string.Join(",", results.Color.DominantColors));
			Console.WriteLine();

			Console.WriteLine("Tipo de imagen:");
			Console.WriteLine("Tipo de clip: " + results.ImageType.ClipArtType);
			Console.WriteLine("Tipo de dibujo/linea: " + results.ImageType.LineDrawingType);
			Console.WriteLine();
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();
			}

		/// <summary>
		///		Detección de objetos en imagen
		/// </summary>
		public static async Task DetectObjectsUrl(ComputerVisionClient client, string urlImage)
			{
			Console.WriteLine("DETECCIÓN DE OBJETOS");
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();

			Console.WriteLine($"Detectando objetos en imagen: {Path.GetFileName(urlImage)}...");
			Console.WriteLine();

			// Para detectar objetos a partir de una imagen local, tendríamos un código 
			// similar al siguiente:
			// using (Stream stream = File.OpenRead(localImage))
			//	{
			//	DetectResult results = await client.DetectObjectsInStreamAsync(stream);
			//	Console.WriteLine("Objetos detectados:");
			//	...

			DetectResult detectObjectAnalysis = await client.DetectObjectsAsync(urlImage);

			Console.WriteLine("Objetos detectados:");
			foreach (var obj in detectObjectAnalysis.Objects)
				{
				Console.WriteLine($"{obj.ObjectProperty} con valor de confianza {obj.Confidence} en la posición {obj.Rectangle.X}, " +
				  $"{obj.Rectangle.X + obj.Rectangle.W}, {obj.Rectangle.Y}, {obj.Rectangle.Y + obj.Rectangle.H}");
				}
			Console.WriteLine();
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();
			}


		/// <summary>
		///		El reconocimiento de contenido en un dominio específico
		///		permite reconocer puntos de referencia y personalidades
		///		famosas en la imagen
		/// </summary>
		public static async Task DetectDomainSpecific(ComputerVisionClient client, string urlImage, string localImage)
			{
			Console.WriteLine("Detección de contenido específico de dominio");
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();

			// Detect the domain-specific content in a URL image.
			DomainModelResults resultsUrl = await client.AnalyzeImageByDomainAsync("landmarks", urlImage);
			// Display results.
			Console.WriteLine($"Detectando puntos de referencia en la imagen: {Path.GetFileName(urlImage)}...");

			var jsonUrl = JsonConvert.SerializeObject(resultsUrl.Result);
			JObject resultJsonUrl = JObject.Parse(jsonUrl);
			if (resultJsonUrl["landmarks"].Any())
				{
				Console.WriteLine($"Punto de referencia: {resultJsonUrl["landmarks"][0]["name"]} " +
					$"con valor de confianza {resultJsonUrl["landmarks"][0]["confidence"]}.");
				}
			Console.WriteLine();

			// El siguiente fragmento es un ejemplo de detección a partir de una imagen local
			//using (Stream imageStream = File.OpenRead(localImage))
			//	{
			//	// Se puede sustituir la cadena "celebrities" por la cadena "landmarks" para cambiar entre detección
			//	// de puntos de referencia y celebridades.
			//	DomainModelResults resultsLocal = await client.AnalyzeImageByDomainInStreamAsync("celebrities", imageStream);
			//	Console.WriteLine($"Detección de personajes famosos en la imagen: {Path.GetFileName(localImage)}...");

			//	var jsonLocal = JsonConvert.SerializeObject(resultsLocal.Result);
			//	JObject resultJsonLocal = JObject.Parse(jsonLocal);
			//	if (resultJsonLocal["celebrities"].Any())
			//		{
			//		Console.WriteLine($"Personaje famoso: {resultJsonLocal["celebrities"][0]["name"]} " +
			//		  $"con valor de confianza {resultJsonLocal["celebrities"][0]["confidence"]}");
			//		}
			//	}
			//Console.WriteLine();
			}

		public static async Task GenerateThumbnail(ComputerVisionClient client, string urlImage, string localImage)
			{
			Console.WriteLine("GENERACIÓN DE IMÁGENES EN MINIATURA");
			Console.WriteLine("----------------------------------------------------------");
			Console.WriteLine();

			string localSavePath = Path.Combine(Environment.CurrentDirectory, "Thumbnails");
			Directory.CreateDirectory(localSavePath);

			// URL
			Console.WriteLine("Generando miniatura a partir de la imagen...");

			// Al establecer smartCropping a true, permite ajustar el ratio de aspecto de
			// la imagen para centrar el área de interés.
			Stream thumbnailUrl = await client.GenerateThumbnailAsync(60, 60, urlImage, true);

			string imageNameUrl = Path.GetFileName(urlImage);
			string thumbnailFilePathUrl = Path.Combine(localSavePath, imageNameUrl.Insert(imageNameUrl.Length - 4, "_thumb"));

			Console.WriteLine("Guardando miniatura de " + thumbnailFilePathUrl);
			using (Stream file = File.Create(thumbnailFilePathUrl)) { thumbnailUrl.CopyTo(file); }

			Console.WriteLine();

			// El siguiente fragmento es un ejemplo de generación de miniatura a partir de una imagen local
			//Console.WriteLine("Generating thumbnail with local image...");

			//using (Stream imageStream = File.OpenRead(localImage))
			//	{
			//	Stream thumbnailLocal = await client.GenerateThumbnailInStreamAsync(100, 100, imageStream, smartCropping: true);

			//	string imageNameLocal = Path.GetFileName(localImage);
			//	string thumbnailFilePathLocal = Path.Combine(localSavePath,
			//			imageNameLocal.Insert(imageNameLocal.Length - 4, "_thumb"));

			//	Console.WriteLine("Saving thumbnail from local image to " + thumbnailFilePathLocal);
			//	using (Stream file = File.Create(thumbnailFilePathLocal)) { thumbnailLocal.CopyTo(file); }
			//	}
			//Console.WriteLine();
			//}
			}
		}
	}