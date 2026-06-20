using System.Text.Json;
using System.Text.RegularExpressions;

namespace Game.Persistence;

public sealed record SaveEnvelope(int Version, Dictionary<string, object?> Data);

public interface IFileSystem
{
    Task WriteAllTextAsync(string path, string contents, CancellationToken cancellationToken);
    Task<string> ReadAllTextAsync(string path, CancellationToken cancellationToken);
    void MoveReplace(string source, string destination);
    bool Exists(string path);
    void Delete(string path);
}

public sealed class SaveRepository
{
    private static readonly Regex SlotPattern = new(
        "^[A-Za-z0-9_-]+$",
        RegexOptions.CultureInvariant
    );
    private readonly IFileSystem files;
    private readonly string root;

    public SaveRepository(IFileSystem files, string root)
    {
        this.files = files ?? throw new ArgumentNullException(nameof(files));
        this.root = root ?? throw new ArgumentNullException(nameof(root));
    }

    public async Task SaveAsync(string slot, SaveEnvelope save, CancellationToken cancellationToken)
    {
        string path = PathFor(slot);
        string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            string json = JsonSerializer.Serialize(new SaveEnvelope(
                2,
                DeepClone(save.Data)
            ));
            await files.WriteAllTextAsync(temporary, json, cancellationToken);
            cancellationToken.ThrowIfCancellationRequested();
            files.MoveReplace(temporary, path);
        }
        catch
        {
            if (files.Exists(temporary)) files.Delete(temporary);
            throw;
        }
    }

    public async Task<SaveEnvelope> LoadAsync(string slot, CancellationToken cancellationToken)
    {
        string json = await files.ReadAllTextAsync(PathFor(slot), cancellationToken);
        using JsonDocument document = JsonDocument.Parse(json);
        int version = document.RootElement.GetProperty("Version").GetInt32();
        if (version < 1 || version > 2) throw new InvalidDataException("unsupported save version");
        var data = (Dictionary<string, object?>)ConvertElement(
            document.RootElement.GetProperty("Data")
        )!;
        if (version == 1 && data.Remove("coins", out object? coins))
        {
            data["currency"] = coins;
        }
        return new SaveEnvelope(2, data);
    }

    private string PathFor(string slot)
    {
        if (slot is null || !SlotPattern.IsMatch(slot)) {
            throw new ArgumentException("invalid save slot", nameof(slot));
        }
        return Path.Combine(root, slot + ".json");
    }

    private static Dictionary<string, object?> DeepClone(Dictionary<string, object?> data)
    {
        using JsonDocument document = JsonDocument.Parse(JsonSerializer.Serialize(data));
        return (Dictionary<string, object?>)ConvertElement(document.RootElement)!;
    }

    private static object? ConvertElement(JsonElement element) => element.ValueKind switch
    {
        JsonValueKind.Object => element.EnumerateObject().ToDictionary(
            property => property.Name,
            property => ConvertElement(property.Value)
        ),
        JsonValueKind.Array => element.EnumerateArray().Select(ConvertElement).ToList(),
        JsonValueKind.String => element.GetString(),
        JsonValueKind.Number when element.TryGetInt64(out long integer) => integer,
        JsonValueKind.Number => element.GetDouble(),
        JsonValueKind.True => true,
        JsonValueKind.False => false,
        JsonValueKind.Null => null,
        _ => throw new InvalidDataException("unsupported JSON value"),
    };
}

public sealed class SaveBridge : Godot.Node
{
    public SaveRepository? Repository { get; set; }
}
