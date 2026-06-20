#pragma once

#include <array>
#include <cstdint>
#include <functional>
#include <stdexcept>

namespace emu {

enum class Access { Read, Write, Execute };
enum Permission : std::uint8_t { R = 1, W = 2, X = 4 };

class MemoryFault : public std::runtime_error {
public:
    MemoryFault(std::uint16_t address, Access access, const char* message);
    std::uint16_t address() const noexcept { return address_; }
    Access access() const noexcept { return access_; }
private:
    std::uint16_t address_;
    Access access_;
};

struct MmioDevice {
    std::function<std::uint32_t(std::uint16_t, unsigned)> read;
    std::function<void(std::uint16_t, unsigned, std::uint32_t)> write;
};

class MemoryBus {
public:
    static constexpr std::uint32_t page_size = 256;
    void map_page(std::uint8_t virtual_page, std::uint8_t physical_page, std::uint8_t permissions);
    void unmap_page(std::uint8_t virtual_page);
    void map_mmio(std::uint16_t first, std::uint16_t last, MmioDevice device);

    std::uint8_t read8(std::uint16_t address, Access access = Access::Read);
    std::uint16_t read16(std::uint16_t address, Access access = Access::Read);
    std::uint32_t read32(std::uint16_t address, Access access = Access::Read);
    void write8(std::uint16_t address, std::uint8_t value);
    void write16(std::uint16_t address, std::uint16_t value);
    void write32(std::uint16_t address, std::uint32_t value);
    std::uint32_t fetch_add32(std::uint16_t address, std::uint32_t value);
    std::uint64_t cycles() const noexcept { return cycles_; }

private:
    struct Mapping { bool valid = false; std::uint8_t physical = 0; std::uint8_t permissions = 0; };
    std::array<Mapping, 256> pages_{};
    std::array<Mapping, 256> tlb_{};
    std::array<std::uint8_t, 65536> ram_{};
    bool has_mmio_ = false;
    std::uint16_t mmio_first_ = 0;
    std::uint16_t mmio_last_ = 0;
    MmioDevice mmio_{};
    std::uint64_t cycles_ = 0;

    std::uint16_t translate(std::uint16_t address, Access access);
};

}
