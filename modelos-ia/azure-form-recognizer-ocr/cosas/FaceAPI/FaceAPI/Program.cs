using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;

namespace FaceAPI
	{
	public class Program
		{
		#region Shared input data

		// From your Face subscription in the Azure portal, get your subscription key and endpoint.
		private const string SubscriptionKey = "b0df5fa0e120457fa9096f0dd0cfe3f7";
		private const string Endpoint = "https://cursoiabd-faceapi.cognitiveservices.azure.com/";

		private static IFaceClient _faceApiClient;
		private static IFaceClient FaceApiClient
			{
			get
				{
				if (_faceApiClient == null)
					{
					_faceApiClient = new FaceClient(new ApiKeyServiceClientCredentials(SubscriptionKey)) { Endpoint = Endpoint };
					}

				return _faceApiClient;
				}
			}

		private const string ImageBaseUrl = "https://csdx.blob.core.windows.net/resources/Face/Images/";

		#endregion Shared input data

		#region Featurization input data

		private static List<string> MiscelaneousImagesUrls 
			{
			get
				{
				return new List<string>()
					{
					new Uri(new Uri(ImageBaseUrl),"detection1.jpg").ToString(),    // single female with glasses
					// new Uri(new Uri(ImageBaseUrl),"detection2.jpg").ToString(), // (optional: single man)
					// new Uri(new Uri(ImageBaseUrl),"detection3.jpg").ToString(), // (optional: single male construction worker)
					// new Uri(new Uri(ImageBaseUrl),"detection4.jpg").ToString(), // (optional: 3 people at cafe, 1 is blurred)
					new Uri(new Uri(ImageBaseUrl),"detection5.jpg").ToString(),    // family, woman child man
					new Uri(new Uri(ImageBaseUrl),"detection6.jpg").ToString()     // elderly couple, male female
					};
				}
			}

		public static readonly List<FaceAttributeType> _requestedFaceAttribs = new()
			{
			FaceAttributeType.Accessories,
			FaceAttributeType.Age,
			FaceAttributeType.Blur,
			FaceAttributeType.Emotion,
			FaceAttributeType.Exposure,
			FaceAttributeType.FacialHair,
			FaceAttributeType.Glasses,
			FaceAttributeType.Hair,
			FaceAttributeType.HeadPose,
			FaceAttributeType.Makeup,
			FaceAttributeType.Noise,
			FaceAttributeType.Occlusion,
			FaceAttributeType.Smile,
			FaceAttributeType.Smile,
			FaceAttributeType.QualityForRecognition
			};

		#endregion Featurization input data

		#region Finder input data

		private static readonly string _sourceImageUrl = new Uri(new Uri(ImageBaseUrl), "findsimilar.jpg").ToString();

		private static List<string> SimilarImagesUrls
			{
			get
				{
				return new List<string>
					{
					new Uri(new Uri(ImageBaseUrl), "Family1-Dad1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family1-Daughter1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family1-Mom1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family1-Son1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family2-Lady1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family2-Man1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family3-Lady1.jpg").ToString(),
					new Uri(new Uri(ImageBaseUrl), "Family3-Man1.jpg").ToString(),
					};
				}
			}

		#endregion Finder input data

		public static async Task Main(string[] args)
			{
			//await AnalyzeFacesAsync();
			await FindSimilarFacesAsync();
			}

		private static async Task AnalyzeFacesAsync()
			{
			FaceFeaturizator featurizator = new(FaceApiClient);

			foreach (string imageUrl in MiscelaneousImagesUrls)
				{
				await featurizator.AnalyzeFacesInImageAsync(imageUrl, false, _requestedFaceAttribs);
				}
			}

		private static async Task FindSimilarFacesAsync()
			{
			SimilarFaceFinder finder = new(FaceApiClient);
			await finder.FindSimilarFacesAsync(_sourceImageUrl, SimilarImagesUrls);
			}
		}
	}
