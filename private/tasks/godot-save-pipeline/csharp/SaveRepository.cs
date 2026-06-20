using System.Text.Json;

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
    private readonly IFileSystem files;
    private readonly string root;

    public SaveRepository(IFileSystem files, string root)
    {
        this.files = files;
        this.root = root;
    }

    public async Task SaveAsync(string slot, SaveEnvelope save, CancellationToken cancellationToken)
    {
        var path = Path.Combine(root, slot + ".json");
        await files.WriteAllTextAsync(path, JsonSerializer.Serialize(save), cancellationToken);
    }

    public async Task<SaveEnvelope> LoadAsync(string slot, CancellationToken cancellationToken)
    {
        var path = Path.Combine(root, slot + ".json");
        return JsonSerializer.Deserialize<SaveEnvelope>(
            await files.ReadAllTextAsync(path, cancellationToken)
        )!;
    }
}

public sealed class SaveBridge : Godot.Node
{
    public SaveRepository? Repository { get; set; }
}
