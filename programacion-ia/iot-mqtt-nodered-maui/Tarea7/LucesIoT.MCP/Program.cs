using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelContextProtocol.Server;
using LucesIoT.MCP;

// Servidor MCP para controlar luces IoT
// Sigo el mismo patron que el ejemplo de MovieManagementSystem
var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddHttpClient<NodeRedApiService>();
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

Console.WriteLine("=== LucesIoT - Servidor MCP ===");
Console.WriteLine("Esperando conexiones...");

await builder.Build().RunAsync();
